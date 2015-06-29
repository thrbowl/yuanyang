# -*- coding: utf-8 -*-
import datetime
from functools import wraps
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin
from flask import current_app, jsonify
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Boolean, Text, DateTime, Date, Float, desc
from sqlalchemy.orm import relationship, backref
from ..message import ERROR_MESSAGE


db = SQLAlchemy()
settings = current_app.config


def catch_db_error(func):
    @wraps(func)
    def _catch_db_error(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception, e:
            db.session.rollback()
            return jsonify(ERROR_MESSAGE)
        finally:
            db.session.remove()

    return _catch_db_error


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

supplier_business_scopes = Table(
    'supplier_business_scopes',
    db.metadata,
    Column('id', Integer, primary_key=True),
    Column('supplier_id', Integer, ForeignKey('suppliers.id'), nullable=False),
    Column('business_scope_id', Integer, ForeignKey('business_scopes.id'), nullable=False)
)


class Area(db.Model):
    """地区"""
    __tablename__ = 'areas'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 地区名称
    full_name = Column(String(100), nullable=False)  # 全路径名称
    parent = Column(Integer, ForeignKey('areas.id'))  # 上级地区
    tree_path = Column(String(100), nullable=False)
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, name, full_name, tree_path):
        self.name = name
        self.full_name = full_name
        self.tree_path = tree_path
        self.create_date = datetime.datetime.now()


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(32), nullable=False, unique=True)
    password = Column(String(64), nullable=False)
    _is_active = Column('is_active', Boolean, nullable=False, default=True)
    is_backend = Column(Boolean, nullable=False, default=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    area_id = Column(Integer, ForeignKey('areas.id'))
    last_login = Column(DateTime, nullable=False)
    create_date = Column(DateTime, nullable=False)

    buildings = relationship('Building', secondary=user_buildings,
                             order_by='desc(Building.create_date)')
    area = relationship('Area', backref=backref('users', order_by=desc(create_date)))

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.create_date = self.last_login = datetime.datetime.now()
        self._is_active = True

    @property
    def name(self):
        return self.username

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

    def get_project_drafts(self):
        return Project.query.filter(Project.user_id == self.id, Project._status == Project.STATUS_DRAFT).all()


class Building(db.Model):
    """楼盘"""
    __tablename__ = 'buildings'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 楼盘名称
    _logo = Column('logo', String(100), nullable=False)  # 楼盘logo图
    address = Column(String(100), nullable=False, default='')  # 楼盘地址
    area_id = Column(Integer, ForeignKey('areas.id'), nullable=False)  # 楼盘所在地区
    create_date = Column(DateTime, nullable=False)

    area = relationship('Area', backref=backref('buildings',
                                                order_by='desc(Building.create_date)',
                                                cascade="all, delete"))
    users = relationship('User', secondary=user_buildings, order_by='desc(User.create_date)')

    def __init__(self, name):
        self.name = name
        self.create_date = datetime.datetime.now()

    def get_logo(self):
        return self._logo or settings['BUILDING_LOGO_DEFAULT']

    def set_logo(self, logo):
        self._logo = logo

    logo = property(get_logo, set_logo)

    @property
    def project_total(self):
        return Project.query.filter(Project.building_id == self.id, Project._status != Project.STATUS_DRAFT).count()

    @property
    def bidding_project_total(self):
        return Project.query.filter(Project.building_id == self.id, Project._status == Project.STATUS_BIDDING).count()


class BusinessScope(db.Model):
    """经营范围"""
    __tablename__ = 'business_scopes'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 分类名称
    parent_id = Column(Integer, ForeignKey('business_scopes.id'))  # 上级分类
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    children = relationship('BusinessScope', cascade="all, delete-orphan", backref=backref('parent', remote_side=[id]),
                            order_by='desc(BusinessScope.order_num),desc(BusinessScope.create_date)')

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
    email = Column(String(100), nullable=False)  # 邮箱地址
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    _status = Column('status', Integer, nullable=False, default=STATUS_NOTAUTH)  # 状态
    company_name = Column(String(100))  # 企业名称
    company_contact = Column(String(100))  # 企业联系人
    company_contact_telephone = Column(String(100))  # 联系人电话
    company_area_id = Column(Integer, ForeignKey('areas.id'))  # 公司所在地
    company_address = Column(String(100))  # 公司详细地址
    deposit_bank = Column(String(100))  # 开户银行
    bank_account = Column(String(100))  # 银行帐号
    business_licence = Column(String(100))  # 营业执照
    business_licence_image = Column(String(100))  # 营业执照图
    tax_registration_certificate = Column(String(100))  # 税务登记证
    tax_registration_certificate_image = Column(String(100))  # 税务登记证图
    organization_code_certificate = Column(String(100))  # 组织结构代码证
    organization_code_certificate_image = Column(String(100))  # 组织结构代码证图
    cost_score = Column(Float, nullable=False, default=0)
    quality_score = Column(Float, nullable=False, default=0)
    time_score = Column(Float, nullable=False, default=0)
    service_score = Column(Float, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    user = relationship('User', backref=backref('supplier', uselist=False, cascade="all, delete"))
    business_scopes = relationship('BusinessScope', secondary=supplier_business_scopes,
                                   order_by='desc(BusinessScope.order_num),desc(BusinessScope.create_date)')
    area = relationship('Area', backref=backref('suppliers',
                                                order_by='desc(Supplier.create_date)',
                                                cascade="all, delete"))

    def __init__(self, user, email):
        self.email = email
        self.user = user
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

    def is_bid(self, project_id):
        return Bid.query.filter(Bid.project_id == project_id, Bid.supplier_id == self.id).count() > 0


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
    name = Column(String(100))  # 项目名称
    building_id = Column(Integer, ForeignKey('buildings.id'), nullable=False)  # 所属楼盘
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 创建者
    type_id = Column(Integer, ForeignKey('business_scopes.id'), nullable=False)  # 项目类型
    supplier_id = Column(Integer)  # 中标供应商
    bid_id = Column(Integer)  # 投标ID
    _status = Column('status', Integer, nullable=False, default=STATUS_DRAFT)  # 项目状态
    due_date = Column(Date)  # 截止时间
    completed_date = Column(Date)  # 完成时间
    publish_date = Column(DateTime)  # 发布时间
    lead_start_date = Column(Date)  # 交付起始时间
    lead_end_date = Column(Date)  # 交付完成时间
    _price_range = Column('price_range', Integer, nullable=False)  # 报价区间
    requirements = Column(Text)  # 项目需求
    create_date = Column(DateTime, nullable=False)

    building = relationship('Building', backref=backref('projects', order_by=due_date.desc(), cascade="all, delete"))
    business_scope = relationship('BusinessScope')

    def __init__(self):
        self.create_date = datetime.datetime.now()

    def get_status(self):
        if self._status == Project.STATUS_DRAFT:
            return Project.STATUS_DRAFT
        elif self._status == Project.STATUS_BIDDING:
            today = datetime.date.today()
            if today > self.due_date:
                self.status = Project.STATUS_ENDED
                db.session.commit()
                return self.status
            return Project.STATUS_BIDDING
        elif self._status == Project.STATUS_ENDED:
            return Project.STATUS_ENDED
        elif self._status == Project.STATUS_COMPLETED:
            if not self.is_closure_period():
                self.status = Project.STATUS_COMMENTED
                db.session.commit()
                return self.status
            return Project.STATUS_COMPLETED
        elif self._status == Project.STATUS_COMMENTED:
            return Project.STATUS_COMMENTED
        elif self._status == Project.STATUS_FAILURE:
            return Project.STATUS_FAILURE

    def set_status(self, status):
        self._status = status

    status = property(get_status, set_status)

    def get_price_range(self):
        if self._price_range == Project.PRICE_RANGE_0_5W:
            return Project.PRICE_RANGE_0_5W
        elif self._price_range == Project.PRICE_RANGE_5_10W:
            return Project.PRICE_RANGE_5_10W
        elif self._price_range == Project.PRICE_RANGE_10_20W:
            return Project.PRICE_RANGE_10_20W
        elif self._price_range == Project.PRICE_RANGE_20_30W:
            return Project.PRICE_RANGE_20_30W
        elif self._price_range == Project.PRICE_RANGE_30_50W:
            return Project.PRICE_RANGE_30_50W
        elif self._price_range == Project.PRICE_RANGE_100_XW:
            return Project.PRICE_RANGE_100_XW

    def set_price_range(self, price_range):
        self._price_range = price_range

    price_range = property(get_price_range, set_price_range)

    def publish(self):
        if self.status == Project.STATUS_DRAFT and self.is_completed():
            self.status = Project.STATUS_BIDDING
            self.publish_date = datetime.datetime.now()
            return True
        return False

    def is_completed(self):
        if self.name and self.due_date and self.lead_start_date and self.lead_end_date:
            return True
        return False

    def is_closure_period(self):
        today = datetime.date.today()
        return self.status == self.STATUS_COMPLETED \
               and today < self.due_date + datetime.timedelta(settings['CLOSURE_PERIOD'])


PROJECT_PRICE_RANGE_LIST = [
    Project.PRICE_RANGE_0_5W,
    Project.PRICE_RANGE_5_10W,
    Project.PRICE_RANGE_10_20W,
    Project.PRICE_RANGE_20_30W,
    Project.PRICE_RANGE_30_50W,
    Project.PRICE_RANGE_100_XW
]

PROJECT_STATUS_LIST = [
    Project.STATUS_BIDDING,
    Project.STATUS_COMPLETED,
    Project.STATUS_COMMENTED,
    Project.STATUS_ENDED,
    Project.STATUS_FAILURE
]


class Carousel(db.Model):
    """轮播"""
    __tablename__ = 'carousels'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # 名称
    _image = Column('image', String(100), nullable=False)  # 轮播图
    url = Column(String(100), nullable=False, default='')  # 链接地址
    description = Column(Text)  # 描述
    order_num = Column(Integer, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.create_date = datetime.datetime.now()

    def get_image(self):
        return self._image or settings['CAROUSEL_IMG_DEFAULT']

    def set_image(self, image):
        self._image = image

    image = property(get_image, set_image)


class StartPage(db.Model):
    """启动页"""
    __tablename__ = 'startpages'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    _image = Column('image', String(100), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.create_date = datetime.datetime.now()

    def get_image(self):
        return self._image or settings['STARTPAGE_IMG_DEFAULT']

    def set_image(self, image):
        self._image = image

    image = property(get_image, set_image)


class Message(db.Model):
    """消息"""
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    content = Column(String(500), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), default=None)
    receiver_id = Column(Integer, ForeignKey('users.id'), default=None)
    is_read = Column(Boolean, nullable=False, default=False)
    read_date = Column(DateTime, nullable=False)
    create_date = Column(DateTime, nullable=False)

    def __init__(self, content):
        self.content = content
        self.create_date = datetime.datetime.now()

    def read(self):
        if not self.is_read:
            self.is_read = True
            self.read_date = datetime.datetime.now()
            return True
        return False

    @staticmethod
    def send_user_msg(sender_id, receiver_id, msg_tpl, **data):
        content = msg_tpl % data
        message = Message(content)
        message.sender_id = sender_id
        message.receiver_id = receiver_id
        db.session.add(message)

    @staticmethod
    def send_system_msg(sender_id, receiver_id, msg_tpl, **data):
        content = msg_tpl % data
        message = Message(content)
        message.sender_id = sender_id
        message.receiver_id = receiver_id
        db.session.add(message)


class Comment(db.Model):
    """评价"""
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    content = Column(String(500), nullable=False)
    cost_score = Column(Float, nullable=False, default=0)
    quality_score = Column(Float, nullable=False, default=0)
    time_score = Column(Float, nullable=False, default=0)
    service_score = Column(Float, nullable=False, default=0)
    create_date = Column(DateTime, nullable=False)


class Bid(db.Model):
    """投标"""
    __tablename__ = 'bids'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    email = Column(String(100), nullable=False)
    company_contact = Column(String(100))
    company_contact_telephone = Column(String(100))
    summary = Column(Text)
    create_date = Column(DateTime, nullable=False)

    project = relationship('Project', backref=backref('bids', order_by=create_date.desc(), cascade="all, delete"))
    supplier = relationship('Supplier', backref=backref('bids', order_by=create_date.desc(), cascade="all, delete"))

    def __init__(self):
        self.create_date = datetime.datetime.now()
