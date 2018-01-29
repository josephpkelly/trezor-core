from trezor.crypto import bip32

from trezor.messages.MultisigRedeemScriptType import MultisigRedeemScriptType
from trezor.messages.HDNodePathType import HDNodePathType

from apps.wallet.sign_tx.writers import *


def multisig_get_pubkey(hd: HDNodePathType) -> bytes:
    p = hd.address_n
    n = hd.node
    node = bip32.HDNode(
        depth=n.depth,
        fingerprint=n.fingerprint,
        child_num=n.child_num,
        chain_code=n.chain_code,
        public_key=n.public_key)
    for i in p:
        node.derive(i, True)
    return node.public_key()


def multisig_get_pubkeys(multisig: MultisigRedeemScriptType):
    return [multisig_get_pubkey(hd) for hd in multisig.pubkeys]