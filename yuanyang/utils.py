# -*- coding: utf-8 -*-
import hashlib
import base64
import random
import string
from PIL import Image


SALT_CHARS = string.ascii_letters + string.digits


def remove_if_endswith(str, *args):
    """Remove the specified string in list when it endswith the string"""
    for suffix in args:
        if str.endswith(suffix):
            return str[:-len(suffix)]
    return str


def remove_if_startwith(str, *args):
    """Remove the specified string in list when it startswith the string"""
    for prefix in args:
        if str.startswith(prefix):
            return str[len(prefix):]
    return str


def rand_generator(size=6, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def generate_hash_salt(password, method='sha1', hash_encoding='base64', salt_length=8, salt=None):
    """Generate the has and salt for given password"""
    salt = salt or ''.join(
        (random.choice(SALT_CHARS) for i in range(salt_length))
    )
    hash_method = getattr(hashlib, method)
    hash = hash_method((password + salt).encode('utf-8')).digest()
    if hash_encoding is None:
        enc_method = lambda x: x
    elif hash_encoding[:4] == 'base':
        def enc_method(value):
            base_method = getattr(
                base64, 'b{0}encode'.format(hash_encoding[4:])
            )
            return base_method(value).decode('ascii')
    return enc_method(hash), salt


def check_image_size(filepath, width, height):
    im = Image.open(filepath)
    im.close()
    return im.size == (width, height)
