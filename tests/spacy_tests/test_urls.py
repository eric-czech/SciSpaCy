# coding: utf-8
from __future__ import unicode_literals

import pytest
import spacy

URLS_BASIC = [
    "http://www.nytimes.com/2016/04/20/us/politics/new-york-primary-preview.html?hp&action=click&pgtype=Homepage&clickSource=story-heading&module=a-lede-package-region&region=top-news&WT.nav=top-news&_r=0",
    "www.red-stars.com",
    "mailto:foo.bar@baz.com",

]

URLS_FULL = URLS_BASIC + [
    "mailto:foo-bar@baz-co.com",
    "www.google.com?q=google",
    "http://foo.com/blah_(wikipedia)#cite-1"
]

# URL SHOULD_MATCH and SHOULD_NOT_MATCH patterns courtesy of https://mathiasbynens.be/demo/url-regex
URLS_SHOULD_MATCH = [
    "http://foo.com/blah_blah",
    "http://foo.com/blah_blah/",
    "http://www.example.com/wpstyle/?p=364",
    "https://www.example.com/foo/?bar=baz&inga=42&quux",
    "http://userid:password@example.com:8080",
    "http://userid:password@example.com:8080/",
    "http://userid@example.com",
    "http://userid@example.com/",
    "http://userid@example.com:8080",
    "http://userid@example.com:8080/",
    "http://userid:password@example.com",
    "http://userid:password@example.com/",
    "http://142.42.1.1/",
    "http://142.42.1.1:8080/",
    "http://foo.com/blah_(wikipedia)#cite-1",
    "http://foo.com/blah_(wikipedia)_blah#cite-1",
    "http://foo.com/unicode_(✪)_in_parens",
    "http://foo.com/(something)?after=parens",
    "http://code.google.com/events/#&product=browser",
    "http://j.mp",
    "ftp://foo.bar/baz",
    "http://foo.bar/?q=Test%20URL-encoded%20stuff",
    "http://-.~_!$&'()*+,;=:%40:80%2f::::::@example.com",
    "http://1337.net",
    "http://a.b-c.de",
    "http://223.255.255.254",
    "http://a.b--c.de/", # this is a legit domain name see: https://gist.github.com/dperini/729294 comment on 9/9/2014

    pytest.param("http://foo.com/blah_blah_(wikipedia)", marks=pytest.mark.xfail),
    pytest.param("http://foo.com/blah_blah_(wikipedia)_(again)", marks=pytest.mark.xfail),
    pytest.param("http://⌘.ws", marks=pytest.mark.xfail),
    pytest.param("http://⌘.ws/", marks=pytest.mark.xfail),
    pytest.param("http://☺.damowmow.com/", marks=pytest.mark.xfail),
    pytest.param("http://✪df.ws/123", marks=pytest.mark.xfail),
    pytest.param("http://➡.ws/䨹", marks=pytest.mark.xfail),
    pytest.param("http://مثال.إختبار", marks=pytest.mark.xfail),
    pytest.param("http://例子.测试", marks=pytest.mark.xfail),
    pytest.param("http://उदाहरण.परीक्षा", marks=pytest.mark.xfail),
]

URLS_SHOULD_NOT_MATCH = [
    "http://",
    "http://.",
    "http://..",
    "http://../",
    "http://?",
    "http://??",
    "http://??/",
    "http://#",
    "http://##",
    "http://##/",
    "http://foo.bar?q=Spaces should be encoded",
    "//",
    "//a",
    "///a",
    "///",
    "http:///a",
    "rdar://1234",
    "h://test",
    "http:// shouldfail.com",
    ":// should fail",
    "http://foo.bar/foo(bar)baz quux",
    "ftps://foo.bar/",
    "http://-error-.invalid/",
    "http://a.b-.co",
    "http://0.0.0.0",
    "http://10.1.1.0",
    "http://10.1.1.255",
    "http://224.1.1.1",
    "http://123.123.123",
    "http://3628126748",
    "http://.www.foo.bar/",
    "http://.www.foo.bar./",
    "http://10.1.1.1",
    "NASDAQ:GOOG",

    pytest.param("foo.com", marks=pytest.mark.xfail),
    pytest.param("http://1.1.1.1.1", marks=pytest.mark.xfail),
    pytest.param("http://www.foo.bar./", marks=pytest.mark.xfail),
    pytest.param("http://-a.b.co", marks=pytest.mark.xfail),
]


# Punctuation we want to check is split away before the URL
PREFIXES = [
    "(", '"', ">"
]


# Punctuation we want to check is split away after the URL
SUFFIXES = [
    '"', ":", ">"]

@pytest.mark.parametrize("url", URLS_SHOULD_MATCH)
def test_should_match(combined_all_model_fixture, url):
    token_match = combined_all_model_fixture.tokenizer.token_match
    if token_match:
        assert token_match(url)

@pytest.mark.parametrize("url", URLS_SHOULD_NOT_MATCH)
def test_should_not_match(combined_all_model_fixture, url):
    token_match = combined_all_model_fixture.tokenizer.token_match
    if token_match:
        assert not token_match(url)

@pytest.mark.parametrize("url", URLS_BASIC)
def test_tokenizer_handles_simple_url(combined_all_model_fixture, url):
    tokens = combined_all_model_fixture(url)
    assert len(tokens) == 1
    assert tokens[0].text == url


@pytest.mark.parametrize("url", URLS_BASIC)
def test_tokenizer_handles_simple_surround_url(combined_all_model_fixture, url):
    tokens = combined_all_model_fixture("(" + url + ")")
    assert len(tokens) == 3
    assert tokens[0].text == "("
    assert tokens[1].text == url
    assert tokens[2].text == ")"


@pytest.mark.parametrize("prefix", PREFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_prefixed_url(combined_all_model_fixture, prefix, url):
    tokens = combined_all_model_fixture(prefix + url)
    assert len(tokens) == 2
    assert tokens[0].text == prefix
    assert tokens[1].text == url


@pytest.mark.parametrize("suffix", SUFFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_suffixed_url(combined_all_model_fixture, url, suffix):
    tokens = combined_all_model_fixture(url + suffix)
    assert len(tokens) == 2
    assert tokens[0].text == url
    assert tokens[1].text == suffix


@pytest.mark.parametrize("prefix", PREFIXES)
@pytest.mark.parametrize("suffix", SUFFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_surround_url(combined_all_model_fixture, prefix, suffix, url):
    tokens = combined_all_model_fixture(prefix + url + suffix)
    assert len(tokens) == 3
    assert tokens[0].text == prefix
    assert tokens[1].text == url
    assert tokens[2].text == suffix


@pytest.mark.parametrize("prefix1", PREFIXES)
@pytest.mark.parametrize("prefix2", PREFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_two_prefix_url(combined_all_model_fixture, prefix1, prefix2, url):
    tokens = combined_all_model_fixture(prefix1 + prefix2 + url)
    assert len(tokens) == 3
    assert tokens[0].text == prefix1
    assert tokens[1].text == prefix2
    assert tokens[2].text == url


@pytest.mark.parametrize("suffix1", SUFFIXES)
@pytest.mark.parametrize("suffix2", SUFFIXES)
@pytest.mark.parametrize("url", URLS_FULL)
def test_tokenizer_handles_two_suffix_url(combined_all_model_fixture, suffix1, suffix2, url):
    tokens = combined_all_model_fixture(url + suffix1 + suffix2)
    assert len(tokens) == 3
    assert tokens[0].text == url
    assert tokens[1].text == suffix1
    assert tokens[2].text == suffix2
