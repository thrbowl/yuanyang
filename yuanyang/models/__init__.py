# -*- coding: utf-8 -*-
import datetime
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from flask import current_app
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean, Text, DateTime, func, and_, select, desc
from sqlalchemy.orm import relationship, relation, backref, object_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()
settings = current_app.config


class _CONS(int):
    def __new__(cls, value, display_name):
        obj = int.__new__(cls, value)
        obj.display_name = display_name
        return obj

    def get_display_name(self):
        return self.display_name


user_buildings = Table(
    'user_buildings',
    db.metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', Integer, ForeignKey('users.id'), nullable=False),
    Column('buildings_id', Integer, ForeignKey('buildings.id'), nullable=False)
)


class Region(db.Model):
    """区域"""
    __tablename__ = 'regions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)  # 地区名称
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, name):
        self.name = name
        self.create_date = datetime.datetime.now()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    _is_active = Column('is_active', Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)
    region_id = Column(Integer, ForeignKey('regions.id'))
    last_login = Column(DateTime, nullable=False)
    create_date = Column(DateTime, nullable=False)

    buildings = relationship('Building', secondary=user_buildings,
                             order_by='desc(Building.order_num),desc(Building.id)')
    region = relationship('Region', backref=backref('users', order_by=desc(create_date)))

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.create_date = self.last_login = datetime.datetime.now()
        self._is_active = True

    def is_active(self):
        return self._is_active

    @staticmethod
    def get(username):
        try:
            user = User.query.filter(User.username == username).one()
            return user
        except:
            pass

    def disable(self):
        self._is_active = False

    def enable(self):
        self._is_active = True


class Area(db.Model):
    """地区"""
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 地区名称
    full_name = Column(String(100), nullable=False)  # 全路径名称
    parent_id = Column(Integer, ForeignKey('areas.id'))  # 上级地区
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, name, full_name):
        self.name = name
        self.full_name = full_name
        self.create_date = datetime.datetime.now()


class Building(db.Model):
    """楼盘"""
    __tablename__ = 'buildings'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 楼盘名称
    logo = Column(String(100), nullable=False)  # 楼盘logo图
    address = Column(String(100), nullable=False, default='')  # 楼盘地址
    region_id = Column(Integer, ForeignKey('regions.id'), nullable=False)  # 楼盘所在地区
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    region = relationship('Region', backref=backref('buildings',
                          order_by='desc(Building.order_num),desc(Building.id)', cascade="all, delete"))
    users = relationship('User', secondary=user_buildings, order_by='desc(User.id)')

    def __init__(self, name):
        self.name = name
        self.create_date = datetime.datetime.now()

    @property
    def project_total(self):
        return Project.query.count()

    @property
    def bidding_project_total(self):
        return Project.query.filter(Project._status == Project.STATUS_BIDDING).count()


class BusinessScope(db.Model):
    """经营范围"""
    __tablename__ = 'business_scopes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 分类名称
    parent_id = Column(Integer, ForeignKey('business_scopes.id'))  # 上级分类
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, name):
        self.name = name
        self.create_date = datetime.datetime.now()


class Supplier(db.Model):
    """供应商"""
    __tablename__ = 'suppliers'

    STATUS_NOTAUTH = _CONS(0, u'未认证')
    STATUS_PENDING = _CONS(1, u'审核中')
    STATUS_REJECTED = _CONS(2, u'认证失败')
    STATUS_PASS = _CONS(3, u'通过认证')

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)  # 登录帐号
    password = Column(String(64), nullable=False)  # 登录密码
    salt = Column(String(8), nullable=False)  # 加密码
    email = Column(String(100), nullable=False)  # 邮箱地址
    _status = Column('status', Integer, nullable=False, default=STATUS_NOTAUTH)  # 状态
    company_name = Column(String(100))  # 企业名称
    company_contact = Column(String(100))  # 企业联系人
    company_contact_telephone = Column(String(100))  # 联系人电话
    company_area_id = Column(Integer, ForeignKey('areas.id'))  # 公司所在地
    company_address = Column(String(100))  # 公司详细地址
    deposit_bank = Column(String(100))  # 开户银行
    bank_account = Column(String(100))  # 银行帐号
    business_licence = Column(String(100))  # 营业执照
    tax_registration_certificate = Column(String(100))  # 税务登记证
    organization_code_certificate = Column(String(100))  # 组织结构代码证
    create_date = Column(DateTime, nullable=False)

    def __init__(self, username, password, salt):
        self.username = username
        self.password = password
        self.salt = salt
        self.create_date = datetime.datetime.now()

    def get_status(self):
        if self._status == Supplier.STATUS_NOTAUTH:
            return Supplier.STATUS_NOTAUTH
        elif self._status == Supplier.STATUS_PENDING:
            return Supplier.STATUS_PENDING
        elif self._status == Supplier.STATUS_REJECTED:
            return Supplier.STATUS_REJECTED
        elif self._status == Supplier.STATUS_PASS:
            return Supplier.STATUS_PASS

    def set_status(self, status):
        self._status = status

    status = property(get_status, set_status)


class Project(db.Model):
    """项目"""
    __tablename__ = 'projects'

    STATUS_DRAFT = _CONS(0, u'草稿')
    STATUS_BIDDING = _CONS(1, u'招标中')
    STATUS_ENDED = _CONS(2, u'已截至')
    STATUS_COMPLETED = _CONS(3, u'已完成')
    STATUS_COMMENTED = _CONS(4, u'已评价')
    STATUS_FAILURE = _CONS(5, u'流标')

    PRICE_RANGE_0_5W = _CONS(1, u'5W以下')
    PRICE_RANGE_5_10W = _CONS(2, u'5W-10W')
    PRICE_RANGE_10_20W = _CONS(3, u'10W-20W')
    PRICE_RANGE_20_30W = _CONS(4, u'20W-30W')
    PRICE_RANGE_30_50W = _CONS(5, u'30W-50W')
    PRICE_RANGE_100_XW = _CONS(6, u'100W以上')

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 项目名称
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)  # 所属楼盘
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 创建者
    type_id = Column(Integer, ForeignKey('business_scopes.id'), nullable=False)  # 项目类型
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))  # 中标供应商
    _status = Column('status', Integer, nullable=False)  # 项目状态
    due_date = Column(DateTime, nullable=False)  # 截止时间
    publish_date = Column(DateTime, nullable=False)  # 发布时间
    lead_start_date = Column(DateTime, nullable=False)  # 交付起始时间
    lead_end_date = Column(DateTime, nullable=False)  # 交付完成时间
    _price_range = Column('price_range', Integer, nullable=False)  # 报价区间
    create_date = Column(DateTime, nullable=False)

    building = relationship('Building', backref=backref('projects', order_by=due_date, cascade="all, delete"))

    def __init__(self):
        self.create_date = datetime.datetime.now()

    def get_status(self):
        if self._status == Project.STATUS_DRAFT:
            return Project.STATUS_DRAFT
        elif self._status == Project.STATUS_BIDDING:
            return Project.STATUS_BIDDING
        elif self._status == Project.STATUS_ENDED:
            return Project.STATUS_ENDED
        elif self._status == Project.STATUS_COMPLETED:
            return Project.STATUS_COMPLETED
        elif self._status == Project.STATUS_COMMENTED:
            return Project.STATUS_COMMENTED
        elif self._status == Project.STATUS_FAILURE:
            return Project.STATUS_FAILURE

    def set_status(self, status):
        self._status = status

    status = property(get_status, set_status)

    def get_price_range(self):
        if self._status == Project.PRICE_RANGE_0_5W:
            return Project.PRICE_RANGE_0_5W
        elif self._status == Project.PRICE_RANGE_5_10W:
            return Project.PRICE_RANGE_5_10W
        elif self._status == Project.PRICE_RANGE_10_20W:
            return Project.PRICE_RANGE_10_20W
        elif self._status == Project.PRICE_RANGE_20_30W:
            return Project.PRICE_RANGE_20_30W
        elif self._status == Project.PRICE_RANGE_30_50W:
            return Project.PRICE_RANGE_30_50W
        elif self._status == Project.PRICE_RANGE_100_XW:
            return Project.PRICE_RANGE_100_XW

    def set_price_range(self, price_range):
        self._price_range = price_range

    price_range = property(get_price_range, set_price_range)


class Carousel(db.Model):
    """轮播"""
    __tablename__ = 'carousels'

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)  # 标题
    image = Column(String(100), nullable=False)  # 轮播图
    url = Column(String(100), nullable=False, default='')  # 链接地址
    description = Column(Text)  # 描述
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, title, image):
        self.title = title
        self.image = image
        self.create_date = datetime.datetime.now()


class Config(db.Model):
    """配置"""
    __tablename__ = 'configs'

    id = Column(Integer, primary_key=True)
    startpage_text1 = Column(String(100), nullable=False)
    startpage_image1 = Column(String(100), nullable=False)

    def __init__(self):
        raise RuntimeError(u'Config is singleton object')


def get_config():
    return Config.query.get(1)


# class Feed(db.Model):
# """动态"""
# __tablename__ = 'feeds'
#
#     id = Column(Integer, primary_key=True)
#     content = Column(String(500), nullable=False)
#
#
# class Comment(db.Model):
#     """评价"""
#     __tablename__ = 'comments'
#
#     id = Column(Integer, primary_key=True)
#     content = Column(String(500), nullable=False)
#     user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
#     bid_id = Column(Integer, ForeignKey('bids.id'), nullable=False)
#     cost_score = Column(Integer, nullable=False, default=0)
#     quality_score = Column(Integer, nullable=False, default=0)
#     time_score = Column(Integer, nullable=False, default=0)
#     service_score = Column(Integer, nullable=False, default=0)
#     create_date = Column(DateTime, nullable=False)
#
#
# class Bid(db.Model):
#     """投标"""
#     __tablename__ = 'bids'
#
#     id = Column(Integer, primary_key=True)
#     project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
