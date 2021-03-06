from trezor import ui, wire


async def layout_apply_settings(ctx, msg):
    from trezor.messages.Success import Success
    from trezor.messages.FailureType import ProcessError
    from trezor.ui.text import Text
    from ..common.confirm import require_confirm
    from ..common import storage

    if msg.homescreen is None and msg.label is None and msg.language is None and msg.use_passphrase is None:
        raise wire.FailureError(ProcessError, 'No setting provided')

    if msg.homescreen is not None:
        await require_confirm(ctx, Text(
            'Change homescreen', ui.ICON_RESET,
            'Do you really want to', 'change homescreen?'))

    if msg.label is not None:
        await require_confirm(ctx, Text(
            'Change label', ui.ICON_RESET,
            'Do you really want to', 'change label to',
            ui.BOLD, '%s' % msg.label,
            ui.NORMAL, '?'))

    if msg.language is not None:
        await require_confirm(ctx, Text(
            'Change language', ui.ICON_RESET,
            'Do you really want to', 'change language to',
            ui.BOLD, '%s' % msg.language,
            ui.NORMAL, '?'))

    if msg.use_passphrase is not None:
        await require_confirm(ctx, Text(
            'Enable passphrase' if msg.use_passphrase else 'Disable passphrase',
            ui.ICON_RESET,
            'Do you really want to',
            'enable passphrase' if msg.use_passphrase else 'disable passphrase',
            'encryption?'))

    storage.load_settings(label=msg.label,
                          use_passphrase=msg.use_passphrase,
                          homescreen=msg.homescreen)

    return Success(message='Settings applied')
