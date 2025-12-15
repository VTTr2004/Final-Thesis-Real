import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import vgg16, VGG16_Weights
from torchvision.models import resnet18, ResNet18_Weights

#------------------------------
# CÁC LỚP CỦA MÔ HÌN
#------------------------------

class TrafficCNN(nn.Module):
    def __init__(self, config):
        # Lấy dữ liệu thông số
        back_bone = config.get('back_bone', 'vgg16')
        input_shape = config.get('input_shape', (1, 64, 64))
        pretrained = config.get('pretrained', True)

        super(TrafficCNN, self).__init__()

        # Tải Thông Số Backbone
        self.load_back_bone(back_bone, input_shape, pretrained)

        # Tự Động Tính Kích Thước Flatten
        with torch.no_grad():
            dummy_input = torch.zeros(1, *input_shape, device = next(self.features.parameters()).device)
            out = self.features(dummy_input)
            self.flatten_dim = out.view(1, -1).size(1)
        
        # Thay đổi classifier để output 3 lớp
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.flatten_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 3)  # output 3 lớp
        )

    def load_back_bone(self, back_bone='vgg16', input_shape = (1, 64, 64), pretrained=True):
        in_channels = input_shape[0]

        # Thông Số Custom
        if back_bone.startswith('custom'):
            self.get_permission(back_bone)
            self.get_custom(back_bone, in_channels)

        # Các Mô Hình Có Sẵn
        elif back_bone == 'vgg16':
            backbone = vgg16(weights=VGG16_Weights.DEFAULT if pretrained else None)
            backbone.features[0] = nn.Conv2d(in_channels, 64, kernel_size=3, padding=1)
            self.features = backbone.features
            if pretrained:
                for param in self.features.parameters():
                    param.requires_grad = False

        elif back_bone == 'resnet18':
            backbone = resnet18(weights=ResNet18_Weights.DEFAULT if pretrained else None)
            if in_channels != 3:
                backbone.conv1 = nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3, bias=False)
            self.features = nn.Sequential(
                backbone.conv1,
                backbone.bn1,
                backbone.relu,
                backbone.maxpool,
                backbone.layer1,
                backbone.layer2,
                backbone.layer3,
                backbone.layer4
            )
            if pretrained:
                for param in self.features.parameters():
                    param.requires_grad = False

    def get_permission(self, back_bone):
        configs = back_bone.split('_')
        check_list = ['norm', 'dr20', 'dr50', 'dr70']
        self.permission = {}
        if len(configs)>1:
            for config in configs[1:]:
                bl = config[:3]
                self.permission[bl] = {}
                for per in check_list:
                    if per in config:
                        self.permission[bl][per] = True

    def add_block(self, in_ch, out_ch, name):
        layers = [nn.Conv2d(in_ch, out_ch, 3, padding=1)]
        # Xem thứ tự của block
        if name == 'bl1':
            layers = [nn.Conv2d(in_ch, out_ch, 5, padding=1)]
        conf = self.permission.get(name, {})
        # Thêm batch-norm
        if conf.get('norm', False):
            layers.append(nn.BatchNorm2d(out_ch))
        layers.append(nn.ReLU())
        # Thêm dropout
        if conf.get('dr20'):
            layers.append(nn.Dropout(0.2))
        elif conf.get('dr50'):
            layers.append(nn.Dropout(0.5))
        elif conf.get('dr70'):
            layers.append(nn.Dropout(0.7))
        layers.append(nn.MaxPool2d(2))
        return layers
    
    def get_custom(self, back_bone, in_channels):
        # Các Lớp Mặc Định
        ft_list = []
        # 1. Block 1
        in_ch = in_channels
        out_ch = 32
        name = 'bl1'
        ft_list += self.add_block(in_ch, out_ch, name)

        # 2. Block 2
        in_ch = 32
        out_ch = 64
        name = 'bl2'
        ft_list += self.add_block(in_ch, out_ch, name)

        # 3. Block 3
        in_ch = 64
        out_ch = 128
        name = 'bl3'
        ft_list += self.add_block(in_ch, out_ch, name)
        self.features = nn.Sequential(*ft_list)

    def __str__(self):
        string = f"Thông Số Flatten: {self.flatten_dim}"
        return string

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

#------------------------------
# LỚP CHÍNH
#------------------------------

class Classifier:
    def __init__(self, config):
        try:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            self.model = TrafficCNN(config)
            checkpoint = torch.load(config.get('model_path', ''), map_location="cpu")
            self.model.load_state_dict(checkpoint['model_state_dict'])
            
            self.model = self.model.to(self.device).float()     # fix
            self.model.eval()
            print('[INFO] 🟢 Model classification initialized successfully')
        except:
            print('[WARNING] ❗ Cant initalized model classification')

    def classify(self, imgs):
        if len(imgs) == 0:
            return []
        img_tensor = torch.stack(imgs).to(self.device, dtype=torch.float32) / 255.0
        
        # Bß║»t ─Éß║ºu Ph├ón Loß║íi
        with torch.no_grad():
            outputs = self.model(img_tensor)
            probs = torch.softmax(outputs, dim=1)
            prebs = torch.argmax(probs, dim=1)
            top_probs = torch.max(probs, dim=1).values
            result = [[pred.item(), prob.item()] for pred, prob in zip(prebs, top_probs)]
            return result