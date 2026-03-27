"""
成就管理模块 - 处理器层（DDD迁移版）
提供成就相关的API处理器
"""

import logging
from typing import Optional, Dict, Any
from tornado.web import RequestHandler
from loguru import logger

from src.interfaces.api.middleware.auth_middleware import auth_required
from src.application.services.achievement_service_simple import AchievementService

logger = logging.getLogger(__name__)


class AchievementHandler(RequestHandler):
    """成就处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    def write_error(self, status_code: int, **kwargs):
        """写入错误响应"""
        exc_info = kwargs.get('exc_info')
        if exc_info:
            error = exc_info[1]
            error_message = str(error)
        else:
            error_message = self._reason
        
        self.set_status(status_code)
        self.write({
            'success': False,
            'error': {
                'code': f'HTTP_{status_code}',
                'message': error_message
            },
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def get(self, achievement_id: Optional[str] = None):
        """
        获取成就或成就列表
        GET /api/v1/achievements - 获取成就列表
        GET /api/v1/achievements/{achievement_id} - 获取单个成就
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if achievement_id:
                # 获取单个成就
                result = await self.achievement_service.get_achievement(achievement_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取成就列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                achievement_type = self.get_argument('type', None)
                difficulty = self.get_argument('difficulty', None)
                
                result = await self.achievement_service.list_achievements(
                    achievement_type=achievement_type,
                    difficulty=difficulty,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get achievement(s) error: {e}")
            self.write_json({'error': str(e)}, 500)


class UserAchievementHandler(RequestHandler):
    """用户成就处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def get(self, user_achievement_id: Optional[str] = None):
        """
        获取用户成就
        GET /api/v1/achievements/user - 获取当前用户成就列表
        GET /api/v1/achievements/user/{user_achievement_id} - 获取单个用户成就
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if user_achievement_id:
                # 获取单个用户成就
                result = await self.achievement_service.get_user_achievement(user_achievement_id, user_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取用户成就列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                status = self.get_argument('status', None)
                
                result = await self.achievement_service.list_user_achievements(
                    user_id=user_id,
                    status=status,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get user achievement(s) error: {e}")
            self.write_json({'error': str(e)}, 500)


class AchievementProgressHandler(RequestHandler):
    """成就进度处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def get(self):
        """
        获取成就进度
        GET /api/v1/achievements/progress
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 获取成就进度
            result = await self.achievement_service.get_achievement_progress(user_id)
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Get achievement progress error: {e}")
            self.write_json({'error': str(e)}, 500)


class UserAchievementStatsHandler(RequestHandler):
    """用户成就统计处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def get(self):
        """
        获取用户成就统计
        GET /api/v1/achievements/stats
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 获取用户成就统计
            result = await self.achievement_service.get_user_achievement_stats(user_id)
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Get user achievement stats error: {e}")
            self.write_json({'error': str(e)}, 500)


class AchievementTriggerHandler(RequestHandler):
    """成就触发处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def post(self):
        """
        触发成就检查
        POST /api/v1/achievements/trigger
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 触发成就检查
            result = await self.achievement_service.trigger_achievement_check(
                user_id=user_id,
                trigger_type=request_data.get('trigger_type'),
                trigger_data=request_data.get('trigger_data', {})
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Trigger achievement check error: {e}")
            self.write_json({'error': str(e)}, 500)


class BadgeHandler(RequestHandler):
    """徽章处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def get(self, badge_id: Optional[str] = None):
        """
        获取徽章
        GET /api/v1/achievements/badges - 获取徽章列表
        GET /api/v1/achievements/badges/{badge_id} - 获取单个徽章
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            if badge_id:
                # 获取单个徽章
                result = await self.achievement_service.get_badge(badge_id)
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 404)
            else:
                # 获取徽章列表
                page = int(self.get_argument('page', '1'))
                limit = int(self.get_argument('limit', '20'))
                badge_type = self.get_argument('type', None)
                rarity = self.get_argument('rarity', None)
                
                result = await self.achievement_service.list_badges(
                    badge_type=badge_type,
                    rarity=rarity,
                    page=page,
                    limit=limit
                )
                
                if result['success']:
                    self.write_json(result['data'])
                else:
                    self.write_json({'error': result['error']}, 400)
                    
        except Exception as e:
            logger.error(f"Get badge(s) error: {e}")
            self.write_json({'error': str(e)}, 500)


class UserBadgeHandler(RequestHandler):
    """用户徽章处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def get(self):
        """
        获取用户徽章
        GET /api/v1/achievements/user/badges
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 获取用户徽章列表
            page = int(self.get_argument('page', '1'))
            limit = int(self.get_argument('limit', '20'))
            
            result = await self.achievement_service.list_user_badges(
                user_id=user_id,
                page=page,
                limit=limit
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Get user badges error: {e}")
            self.write_json({'error': str(e)}, 500)


class RewardHandler(RequestHandler):
    """奖励处理器"""
    
    def initialize(self):
        """初始化处理器"""
        self.achievement_service = AchievementService()
    
    def set_default_headers(self):
        """设置默认响应头"""
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    
    def write_json(self, data: Dict[str, Any], status_code: int = 200):
        """写入JSON响应"""
        self.set_status(status_code)
        self.write({
            'success': status_code < 400,
            'data': data,
            'timestamp': self.request.request_time()
        })
    
    @auth_required
    async def post(self):
        """
        领取奖励
        POST /api/v1/achievements/rewards/claim
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 解析请求数据
            request_data = self.get_json_body()
            
            # 领取奖励
            result = await self.achievement_service.claim_reward(
                user_id=user_id,
                reward_id=request_data.get('reward_id')
            )
            
            if result['success']:
                self.write_json(result['data'])
            else:
                self.write_json({'error': result['error']}, 400)
                
        except Exception as e:
            logger.error(f"Claim reward error: {e}")
            self.write_json({'error': str(e)}, 500)
    
    @auth_required
    async def get(self):
        """
        获取用户奖励
        GET /api/v1/achievements/user/rewards
        """
        try:
            # 获取当前用户
            current_user = self.current_user
            user_id = current_user.get('id') if current_user else None
            
            if not user_id:
                self.write_json({'error': 'User not authenticated'}, 401)
                return
            
            # 获取用户奖励列表
            page = int(self.get_argument('page', '1'))
            limit = int(self.get_argument('limit', '20'))
            reward_type = self.get_argument('type