import factory
from factory.django import DjangoModelFactory
from ostinato.menus.models import Menu, MenuItem


class MenuFactory(DjangoModelFactory):
    slug = factory.Sequence(lambda n: 'menu-{}'.format(n))

    class Meta:
        model = Menu


class MenuItemFactory(DjangoModelFactory):
    title = factory.Sequence(lambda n: 'menu-item-{}'.format(n))

    class Meta:
        models = MenuItem
