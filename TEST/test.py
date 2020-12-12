#!/usr/bin/env python
# coding: utf-8



import requests
import pytest
import conftest


@pytest.mark.parametrize(
    "url,expected",
    [
        ("level=station&net=MN&format=xml&nodata=404",200),
        ("level=network&net=MN&format=xml&nodata=404",200),
        ("level=channelk&net=MN&format=xml&nodata=404",200),
        ("level=response&net=MN&format=xml&nodata=404",200),
    ],
)

def test_eval(url, expected,host):
    response = requests.get( "http://"+host+"/exist/apps/fdsn-station/fdsnws/station/1/query/?" + url)
    print (response.status_code)
    assert response.status_code == expected 



