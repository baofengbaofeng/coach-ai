"""
摄像头设备模型
管理摄像头设备信息、连接状态和配置
"""

from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, Enum, ForeignKey, DateTime, Index
from sqlalchemy.dialects.mysql import CHAR, VARCHAR
from sqlalchemy.orm import relationship

from .base import BaseModel


class CameraDevice(BaseModel):
    """
    摄像头设备模型
    管理摄像头设备信息
    """
    __tablename__ = 'camera_devices'
    
    # 设备名称
    device_name = Column(VARCHAR(100), nullable=False, index=True)
    
    # 设备序列号（唯一标识）
    serial_number = Column(VARCHAR(100), unique=True, nullable=False, index=True)
    
    # 设备类型：webcam, ip_camera, mobile_camera, etc.
    device_type = Column(
        Enum('webcam', 'ip_camera', 'mobile_camera', 'action_camera', 'other', name='camera_type'),
        default='webcam',
        nullable=False
    )
    
    # 设备品牌
    brand = Column(VARCHAR(50), nullable=True)
    
    # 设备型号
    model = Column(VARCHAR(50), nullable=True)
    
    # 设备描述
    description = Column(Text, nullable=True)
    
    # 连接状态：online, offline, error, maintenance
    connection_status = Column(
        Enum('online', 'offline', 'error', 'maintenance', name='connection_status'),
        default='offline',
        nullable=False
    )
    
    # 最后连接时间
    last_connected_at = Column(DateTime, nullable=True)
    
    # 最后断开时间
    last_disconnected_at = Column(DateTime, nullable=True)
    
    # 连接错误信息
    connection_error = Column(Text, nullable=True)
    
    # 设备IP地址
    ip_address = Column(VARCHAR(45), nullable=True, index=True)
    
    # 设备端口
    port = Column(Integer, nullable=True)
    
    # RTSP流地址
    rtsp_url = Column(Text, nullable=True)
    
    # WebRTC信令服务器地址
    webrtc_signaling_url = Column(Text, nullable=True)
    
    # WebRTC Peer ID
    webrtc_peer_id = Column(VARCHAR(100), nullable=True)
    
    # 视频流分辨率
    resolution_width = Column(Integer, default=1920, nullable=False)
    resolution_height = Column(Integer, default=1080, nullable=False)
    
    # 帧率
    frame_rate = Column(Integer, default=30, nullable=False)
    
    # 视频编码格式
    video_codec = Column(VARCHAR(20), default='h264', nullable=False)
    
    # 音频支持
    has_audio = Column(Boolean, default=False, nullable=False)
    
    # 音频编码格式
    audio_codec = Column(VARCHAR(20), nullable=True)
    
    # 设备位置描述
    location = Column(VARCHAR(200), nullable=True)
    
    # 安装角度（度）
    installation_angle = Column(Integer, nullable=True)
    
    # 安装高度（米）
    installation_height = Column(Float, nullable=True)
    
    # 校准数据（JSON格式）
    calibration_data = Column(Text, nullable=True)
    
    # 设备配置（JSON格式）
    device_config = Column(Text, nullable=True)
    
    # 是否启用
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # 是否正在使用
    is_in_use = Column(Boolean, default=False, nullable=False)
    
    # 当前使用者ID
    current_user_id = Column(CHAR(36), ForeignKey('users.id'), nullable=True)
    
    # 当前使用开始时间
    current_use_started_at = Column(DateTime, nullable=True)
    
    # 租户ID（多租户支持）
    tenant_id = Column(CHAR(36), ForeignKey('tenants.id'), nullable=True, index=True)
    
    # 关系
    tenant = relationship('Tenant', backref='camera_devices')
    current_user = relationship('User', foreign_keys=[current_user_id], backref='active_camera_devices')
    
    # 索引
    __table_args__ = (
        Index('idx_camera_device_status', 'connection_status'),
        Index('idx_camera_device_enabled', 'is_enabled'),
        Index('idx_camera_device_in_use', 'is_in_use'),
        Index('idx_camera_device_tenant', 'tenant_id'),
        Index('idx_camera_device_last_connected', 'last_connected_at'),
    )
    
    def __repr__(self):
        return f"<CameraDevice(id='{self.id}', device_name='{self.device_name}', serial='{self.serial_number}')>"
    
    @property
    def resolution(self):
        """
        获取分辨率字符串
        """
        return f"{self.resolution_width}x{self.resolution_height}"
    
    @property
    def is_available(self):
        """
        检查设备是否可用
        """
        return (
            self.is_enabled and 
            self.connection_status == 'online' and 
            not self.is_in_use
        )
    
    @property
    def uptime_minutes(self):
        """
        获取在线时长（分钟）
        """
        if self.last_connected_at and self.connection_status == 'online':
            uptime = (datetime.utcnow() - self.last_connected_at).total_seconds()
            return round(uptime / 60, 2)
        return 0
    
    def connect(self, ip_address=None, port=None):
        """
        连接设备
        """
        self.connection_status = 'online'
        self.last_connected_at = datetime.utcnow()
        self.connection_error = None
        
        if ip_address:
            self.ip_address = ip_address
        if port:
            self.port = port
    
    def disconnect(self, error_message=None):
        """
        断开设备连接
        """
        self.connection_status = 'offline'
        self.last_disconnected_at = datetime.utcnow()
        self.is_in_use = False
        self.current_user_id = None
        self.current_use_started_at = None
        
        if error_message:
            self.connection_error = error_message
    
    def set_error(self, error_message):
        """
        设置设备错误状态
        """
        self.connection_status = 'error'
        self.connection_error = error_message
        self.is_in_use = False
        self.current_user_id = None
        self.current_use_started_at = None
    
    def start_use(self, user_id):
        """
        开始使用设备
        """
        if self.is_available:
            self.is_in_use = True
            self.current_user_id = user_id
            self.current_use_started_at = datetime.utcnow()
            return True
        return False
    
    def end_use(self):
        """
        结束使用设备
        """
        self.is_in_use = False
        self.current_user_id = None
        self.current_use_started_at = None
    
    def get_webrtc_config(self):
        """
        获取WebRTC配置
        """
        config = {
            'peer_id': self.webrtc_peer_id,
            'signaling_url': self.webrtc_signaling_url,
            'video': {
                'width': self.resolution_width,
                'height': self.resolution_height,
                'frameRate': self.frame_rate,
                'codec': self.video_codec
            }
        }
        
        if self.has_audio and self.audio_codec:
            config['audio'] = {
                'codec': self.audio_codec
            }
        
        return config
    
    def get_rtsp_config(self):
        """
        获取RTSP配置
        """
        if not self.rtsp_url:
            return None
        
        return {
            'url': self.rtsp_url,
            'username': None,  # 可以从device_config中解析
            'password': None,  # 可以从device_config中解析
            'resolution': self.resolution,
            'frame_rate': self.frame_rate
        }
    
    def update_calibration(self, calibration_data):
        """
        更新校准数据
        """
        import json
        try:
            # 验证校准数据格式
            if isinstance(calibration_data, dict):
                self.calibration_data = json.dumps(calibration_data)
                return True
        except:
            pass
        return False
    
    def get_calibration(self):
        """
        获取校准数据
        """
        if not self.calibration_data:
            return None
        
        import json
        try:
            return json.loads(self.calibration_data)
        except:
            return None
    
    def to_dict(self):
        """
        转换为字典，包含额外处理
        """
        data = super().to_dict()
        
        # 添加计算属性
        data['resolution'] = self.resolution
        data['is_available'] = self.is_available
        data['uptime_minutes'] = self.uptime_minutes
        
        # 处理JSON字段
        import json
        if self.calibration_data:
            try:
                data['calibration_data'] = json.loads(self.calibration_data)
            except:
                data['calibration_data'] = {}
        else:
            data['calibration_data'] = {}
            
        if self.device_config:
            try:
                data['device_config'] = json.loads(self.device_config)
            except:
                data['device_config'] = {}
        else:
            data['device_config'] = {}
            
        return data
    
    def get_status_summary(self):
        """
        获取状态摘要
        """
        return {
            'device_name': self.device_name,
            'serial_number': self.serial_number,
            'connection_status': self.connection_status,
            'is_available': self.is_available,
            'is_in_use': self.is_in_use,
            'current_user': self.current_user_id,
            'uptime_minutes': self.uptime_minutes,
            'last_connected': self.last_connected_at.isoformat() if self.last_connected_at else None,
            'resolution': self.resolution,
            'frame_rate': self.frame_rate
        }