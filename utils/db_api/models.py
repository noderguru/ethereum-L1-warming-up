from datetime import datetime

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Wallet(Base):
    __tablename__ = 'wallets'

    id: Mapped[int] = mapped_column(primary_key=True)
    private_key: Mapped[str] = mapped_column(unique=True, index=True)
    address: Mapped[str]
    proxy: Mapped[str]
    name: Mapped[str]
    number_of_wrap_unwrap_eth: Mapped[int]
    number_of_swaps: Mapped[int]
    number_of_telepathy: Mapped[int]
    number_of_bungee: Mapped[int]
    number_of_blur: Mapped[int]
    number_of_l2marathon_nft: Mapped[int]
    number_of_merkly_nft: Mapped[int]
    next_initial_action_time: Mapped[datetime | None] = mapped_column(default=None)
    next_activity_action_time: Mapped[datetime | None] = mapped_column(default=None)
    initial_completed: Mapped[bool] = mapped_column(default=False, server_default='0')
    completed: Mapped[bool] = mapped_column(default=False, server_default='0')

    def __repr__(self):
        return f'{self.name}: {self.address}'
