import torch
import torch.nn as nn
import torch.nn.functional as F

class FeatureExtractor(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(FeatureExtractor, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        return self.relu(self.bn(self.conv(x)))

class FeatureFusion(nn.Module):
    def __init__(self, in_channels):
        super(FeatureFusion, self).__init__()
        self.conv1 = nn.Conv2d(in_channels * 2, in_channels, kernel_size=1)
        self.conv2 = nn.Conv2d(in_channels, in_channels, kernel_size=3, padding=1)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, sr_features, ref_features):
        combined = torch.cat((sr_features, ref_features), dim=1)
        out = self.relu(self.conv1(combined))
        return self.relu(self.conv2(out))

class ResidualBlock(nn.Module):
    def __init__(self, in_channels):
        super(ResidualBlock, self).__init__()
        self.conv1 = nn.Conv2d(in_channels, in_channels, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(in_channels)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = nn.Conv2d(in_channels, in_channels, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(in_channels)
        
    def forward(self, x):
        residual = x
        out = self.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        out += residual
        return out

class EnhancerNetwork(nn.Module):
    def __init__(self, in_channels=3, num_residual_blocks=5):
        super(EnhancerNetwork, self).__init__()
        self.feature_extractor_sr = FeatureExtractor(in_channels, 64)
        self.feature_extractor_ref = FeatureExtractor(in_channels, 64)
        
        # Feature fusion layer
        self.feature_fusion = FeatureFusion(64)
        
        # Residual blocks
        self.residual_blocks = nn.Sequential(
            *[ResidualBlock(64) for _ in range(num_residual_blocks)]
        )
        
        # Output layer
        self.output_conv = nn.Conv2d(64, in_channels, kernel_size=3, padding=1)
    
    def forward(self, data_sr_patch, data_ref_patches):
        # Feature extraction from both sr and ref patches
        sr_features = self.feature_extractor_sr(data_sr_patch)
        ref_features = self.feature_extractor_ref(data_ref_patches)
        
        # 배치 크기를 원래대로 되돌리기
        ref_features = ref_features.view(data_sr_patch.size(0), -1, ref_features.size(1), ref_features.size(2), ref_features.size(3))
        ref_features = ref_features.mean(dim=1)  # ref_features를 평균내서 sr_features와 동일한 크기로 맞춤

        # Fusion of the features
        fused_features = self.feature_fusion(sr_features, ref_features)
        
        # Passing through residual blocks
        enhanced_features = self.residual_blocks(fused_features)
        
        # Output enhanced data_sr_patch
        enhanced_data_sr_patch = self.output_conv(enhanced_features)
        return enhanced_data_sr_patch