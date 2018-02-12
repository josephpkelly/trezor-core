from trezor import ui


async def layout_get_address(ctx, msg):
    from trezor.messages.Address import Address
    from ..common import coins
    from ..common import seed
    from ..wallet.sign_tx import addresses

    address_n = msg.address_n or ()
    coin_name = msg.coin_name or 'Bitcoin'
    coin = coins.by_name(coin_name)

    node = await seed.derive_node(ctx, address_n)

    address = addresses.get_address(msg.script_type, coin, node, msg.multisig)

    if msg.show_display:
        await _show_address(ctx, address)

    return Address(address=address)


async def _show_address(ctx, address):
    from trezor.messages.ButtonRequestType import Address
    from trezor.ui.text import Text
    from trezor.ui.qr import Qr
    from trezor.ui.container import Container
    from ..common.confirm import require_confirm

    lines = _split_address(address)
    content = Container(
        Qr(address, (120, 135), 3),
        Text('Confirm address', ui.ICON_RESET, ui.MONO, *lines))
    await require_confirm(ctx, content, code=Address)


def _split_address(address):
    from trezor.utils import chunks
    return chunks(address, 17)
