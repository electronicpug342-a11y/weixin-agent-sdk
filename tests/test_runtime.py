from weixin_agent.media import aes_ecb_padded_size, parse_aes_key
from weixin_agent.runtime import body_from_item_list, markdown_to_plain_text


def test_markdown_to_plain_text() -> None:
    text = "**bold** [link](https://example.com)\n```python\nprint('x')\n```"
    assert markdown_to_plain_text(text) == "bold link\nprint('x')"


def test_body_from_item_list_with_quote() -> None:
    item_list = [
        {
            "type": 1,
            "text_item": {"text": "reply"},
            "ref_msg": {
                "title": "summary",
                "message_item": {
                    "type": 1,
                    "text_item": {"text": "original"},
                },
            },
        }
    ]
    assert body_from_item_list(item_list) == "[Quoted: summary | original]\nreply"


def test_parse_aes_key_supports_raw_and_hex_wrapped_base64() -> None:
    raw_key = bytes.fromhex("00112233445566778899aabbccddeeff")
    raw_b64 = "ABEiM0RVZneImaq7zN3u/w=="
    hex_b64 = "MDAxMTIyMzM0NDU1NjY3Nzg4OTlhYWJiY2NkZGVlZmY="
    assert parse_aes_key(raw_b64) == raw_key
    assert parse_aes_key(hex_b64) == raw_key


def test_aes_padding_size() -> None:
    assert aes_ecb_padded_size(1) == 16
    assert aes_ecb_padded_size(16) == 32
