from nonebot import on_startswith
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import MessageSegment
import os
import re
import time
import json
import aiohttp
from requests_toolbelt.multipart.encoder import MultipartEncoder

'''requirements:
requests_toolbelt
aiohttp
'''

test = on_startswith(msg="百度识图", priority=30)

@test.handle()
async def hanlde_message(bot: Bot, event: Event, state: T_State):
    msg = str(event.message).strip()
    try:
        picurl = getPicUrl(msg)
        if picurl != "":
            await bot.send(event,"识图中...",at_sender=True)
            try:
                os.mkdir("C:\\imageCache\\")
            except Exception as e:
                pass
            picpath = "C:\\imageCache\\" + str(time.time()) + ".jpg"
            async with aiohttp.request("GET",picurl,headers={"Referer":"https://qzone.qq.com/"}) as r:
                ret = await r.read()
            with open(picpath,"wb") as f:
                f.write(ret)
            s = shitu()
            await s.uploadpic(picpath)
            result = await s.getMoreSizePic()
            if result == {} or msg[:4] == "相似图片":
                result = await s.getSimilarPic()
                piclist = "list"
                picwidth = "thumbWidth"
                picheight = "thumbHeight"
                picurltype = 1 # "thumbUrl"
            else:
                piclist = "albumList"
                picwidth = "width"
                picheight = "height"
                picurltype = 0 # "thumbUrl"
            if result["status"] != 0:
                await bot.send(event,"获取图片status不为0")
            else:
                await bot.send(event,"上传图片中...",at_sender=True)
                result = result["data"][piclist]
                tmp = ""
                n = 0
                for x in result:
                    n += 1
                    if picurltype == 1:
                        picurl = x["thumbUrl"]
                    else:
                        picurl = x["imgList"][0]["imgSrc"]
                    picpath = "C:\\imageCache\\" + str(time.time()) + ".jpg"
                    async with aiohttp.request("GET",picurl,headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}) as r:
                        ret = await r.read()
                    with open(picpath,"wb") as f:
                        f.write(ret)
                    tmp = tmp + "宽度：" + str(x[picwidth]) + " 高度：" + str(x[picheight]) + MessageSegment.image("file:///"+picpath)
                    if n >= 5:
                        break
                    tmp = tmp + "\n\n"
                if tmp!="":
                    await bot.send(event,tmp)
    except Exception as e:
        await bot.send(event,"识图时发生错误："+str(e),at_sender=True)


async def myget(url,headers = None):
    async with aiohttp.request("GET",url,headers=headers) as r:
        return await r.text(encoding="utf-8")

async def mypost(url,data = None,headers = None):
    async with aiohttp.request("POST",url,data=data,headers=headers) as r:
        return await r.text(encoding="utf-8")

def getPicUrl(content):
    '''根据文本代码取图片下载地址'''
    searchresult = re.search(",url=(.+?)\]",content,re.I|re.M)
    if searchresult:
        return searchresult.group(1)
    else:
        return ""

class shitu(object):
    def __init__(self):
        self.sdkParams = None
        self.sign = None

    async def getRequestKey(self):
        url = 'https://miao.baidu.com/abdr'
        requestdata = "eyJkYXRhIjoiYjIyY2ZjNjVlZDkxMDE3N2ExNmViYjY0OTNmMWQ5YzUzOGNmZTZiNWNkMzcxNmM1N2UzNzM1NzE2MjQ2MWJiMzQ0M2M3ZTRkZTYyY2Y4NDM5NjY2NDU1M2QxMGM1YWQxNjdlZTNlYjkyZGIxMDAyMjQ2ZGY5YzllYjE1OTNlZjEwMDE5OWJhMzI1NWRhYWUwNzBhNzY0N2YxMWFkZmU0Njg0OTZiZDIyZDBkYjMyODkxNTUwM2YwMGJlMGExYTRmZWE5Mjk1ZTdlMDE5ZjliNzg5ZDJjOWE5ODhlNDZhNmYzY2YxZTcyMzM1YjI5YzE1M2Y4Zjk2MTRjNTRlMDYzYjdmYTBhOTdmNTFlMTQ4ODI4ZTRmOWIyMDBkYzQwMWUxMGU1MjA1MmMyMWUxNjAyNDI5ZTgyMmY2MjBhNjFjOTU2MDE1YmE0Mzg0YjM4OTJjYjliNGZiNzBiMTFjMTdmMjUwMDQzZWY2MTYyNjMxNDczZDk5YmQxNzdjODUzZDFiZTJlMGY4MzI4OGJiYWViYTk2MzMzYmZiYzBhOTY5ODQzYTVkYTUzN2ZkZDliNWUxYzViMmY2NTI1NDM1OGI3ZjU1OTJjN2ZiOTY5ZDcxYzRiNjE0OTZhNTIyOTQwZWM0YzE4N2VlNjQ3MzNlZjIwYjA4NDgzZGY2ZWMyNzY1N2NiODA3ZTMxY2QwODg1ZGM5MDMyODBkZjdhNWZjZmNlZGJiNzBhMjM3YzZmNmExNmY3OWFmOWIxMTZjNDI5NzdiMTEwNDU4MmNiM2Y0MGM5NDkxZDY4OTBmOTQzN2RjMmUwNWE5ZjFkYzM5MjM1MWFmYWI1MWZkNmFjZjYxN2JmYzMwZjYyNmRiZmIwODJjOTQxZGZlOTM0YjhlNTgzNWIxNDQ1NjRkMjJiODRjNDc5ZmNjNDAzZDBlYzhlYjNjMGVmOWU4OTMwYWZhZTVmNzk1ZWUxMjFhZDczNTk2ODgwMzFkOWQxMjJlNWI2YzdiYjIwMTFlMzJiNjE5ZDZmYWQ0MzA3ZDE3OGZiZjMwYzBlYWVkZjllYzBhYzFhMTJlODAzZTFlZDYwYjZhMGM1YTFkMjA5NTMzNmI5ZGE3NTk1MmYxMTBjM2ZhMWNiODBiMjE2MGUzOGU1ZTA1Y2RkMjRjNmMxZmJiYzNkZjdiOGUxODk1ZTJkNTU0NTliNTJhZWU0NTA2NjliNjY2OGQ1ODZjYzQzYTAwMGVkOWZiMGU5MTA3NDU0ZjBhMmRlMTQzN2IwMzJiMGFhOTk5MDZhOTY4MGU3OWExYmFkOGJlNDI2MTgxYjNlZGNjMTY2YTA4NTRmNjE1MjA1MzEwMDExNWE4ZDIxNzVhOTY0YzllMDkzYzRmNTYwYzc0ZTQyZWIxMTQxMTczNjQxNTFkMGRjYjBiNDMwM2QzYWQzNjU5MDExOTJiNGU4YTUxZDQ1ZGZlNDRiMTNhOTY5NjVhNmIyZWNjNDViYTA0ZThiZDU1M2E5ZGQxOTg2Y2Q4N2VkZjJmNDE1YWFlMDY1YmE5YzUzNWU0NGZkYjM3ZGEwODNmMWE4NDYzNTE1MzNhZTkxYjlkNWM2YTliNzAyM2I0ZDYwNjA3OWEwZTcyMTRlODNiMjUyZjg0MzE3NDU0MjU2NTI0MzNmYWE3YjNlZWZlMjNjM2JhYmU3NmM1NzBjNjhiMjA3NmZhMjA1NDY2MzRhZTFkNjJhMTNkZjRmODU2NDAwYWYzYmMxOTVkNWE4YWFlM2IyYjkyMjc5ZWRkMDJmOWQ4NDFiZDViZjBiOTAyYTY1YzEwMGU2YWI1MDhiMGE1ZTgyM2FkNzc0NWQxNjVlYTJiNTZmZmY2OTU5M2IwMDYyZWM3NmU4M2Q4YTQwMTMyYTlkOTIwNjRlZDg4NDUyYTI2MzE1YTRjNGRkMWFlZDJhMjFhZTRlZjY0NmYzNThiNjg0MGE3M2M5YWM4YmYyNzNmYmYwZmVhMTAwNGY3NTY0MWY1OTI3MGUzY2Y2Yjc2OTNjNWI1M2I0ZDMxZWQ2MDU3MTZlMGZkNWI0NzUxY2ZhZTMwNjVkZmRkYjZjNzQ3YjMwYmVmZmNlNGEwNzU3NzBjZWU0NmNjZTkwY2NlZGZjYWQ5ZWRjNmZiMmZjZTBmYzE2YTJiYzFmMTJkMjY5OGM5ZDEyNDRmZWE4ZjViMTBmZTkyYzFlY2Y2MjBjOTI2NGU2NTVkZmY5M2JjY2NmNjYwODVlMzk2YjI1NWRhZWQwNTU2ZThmZWJjOWRlZjc2NDE3ODlmNDEwZGE0MDNkNDVmYThmYWQwOWViNjk0OGIxMDUxMmQyZDUyMzk1ZGNmYmRiNzQ5NmE0NWEwZjc3NTJmNzc3Yjk3ZTdlYzE3NmMwODU5YzdiODFiZjBiYzE5MjhmMTZjM2NjYjViY2JlYThiMWY0ZDgxMmEzMmJlMTIyZDVmNjRmNDcyYjlmZTNiNzNhZmMzYzkyNjE2OTY2OGJjNDdjNWRkOTNmYzlkNjdlZjJmNDQ1NGVjMjNlZTVlM2Q4MmNmNWRhZDk3MGU3MmI0MDJlOGZhOTc5ZDM4ODM4YTU0NTA2YTNlZjdlYTE2MzNiYWZmNmVlMmEyMTA0ZmI5NGE3ZmYwYjcxYmIxY2NkMzYxZjVkYjIyN2I3NDhmNTMxZWQxMDhkYzU1OWQ4YWU1MzNjNGJkYTcwMTE2NDJmNGM1ZjNlZjlmOTFhMjg3ZWI0YmViYTFhZTQ1YTUyNDE0NzI1YzJjZmQ4Zjc1MGY4MTJlODIzOTI5YmMxZmZkMTQ1MWZhOTIxZjFiYmZjMjhkZjhkN2Y3MzkwNjNiMzJlZmIyNjM0NjM0MjkwNzVjMjA2MWI5NjFhMTFkZmMyYzcyMjIyNjZiZjU5OWU4ZjljZjZiZWQ0NWViNmU3NmI1N2ZhN2VhYzg5NjhlYmUxYTljNzlmMzQxNWEyMDNlYzEyNjdhYzExZDkwM2NiODc2YzJhNTY4NjM2NjM1MjA1MjExMDgzNDU0YmQ4NjVkY2MzZWU3NzVmOTdhYjIzZDEwODhiMzdjMGE0ZmViNzg4MjNlOWFlMzE4YTMzNjM0ZGUxM2QzMTc2OGNjOThkZWE2MmFmN2RmYmNlZjM1Mzk3ZmEyMDIzZjE2YzAyYzM2MjVlNDFiY2MwZjAwZmQxMDg4NWU2MGE5YTM2NGRmYjQ1OWRlY2RiZDAyYjJlZTU4MDRlNDFkZDU5NGY1NTg5NGU3MjlmOTJlMTY2ZmYyMWViNGY5Njc1YTEwNzdkMjVhYzUzZDQ3ZjY2MTdjNWNkNGQyOGY4YTY0OTA0Y2Y4ODczYzUzZTM1ZTYzMTczY2U2OGYxMDM5MjNmNmViZGExYWYxZTE5YTMxMzQ1NjI3MGM4ZWY2MzExZWI3ZGUwOGY0YjQxMzRlMmU1OTFkOWJmMzE1Yjg0ZDdmMjdlMmQ4ODI1ZmY1OTY3OTc0OWU1YjIwMmUwZDhiNWRhNDdjYjdkNDdmOWYyNjkzZTJmZmEwZjk5MWZkMzcwMjdjNjU4MDM1ZTk0NTA2MzhlNzE0ZWE5YmViMTNiZWI4NWE1MzkzMmQzMzQ5NDU1ZWY1NWM4N2IyZmZmNzM3MzAxMDhmZjMwMDlmNTUyN2JlOGUyOGIyYTFiNTRiZjFlZDI2NWEyZTU2NTdiODgyY2Y4NmJlOTc3YjI2YjcyMDY2NTgzZDUyOTFhNWEwYzJmY2NiYzMzYWZlMjBkYmJjNzQxYTQ2MDNlNDQyM2Q2NWI5YzgyN2M0MDFlMWY2OTY5ZWFmMjZhMTExYzJjZTMyNWE2OGExMWI5YTA1ZDIwMGQ3NzViZTdmZTQwOGFlZDZiZDg4ZWQ4YWQ5MjU3NTAyIiwia2V5X2lkIjoiMzI0YTg0MzAzYzllNDNmYiJ9"
        ret = await mypost(url, data=requestdata)
        self.sdkParams = ret
        return ret

    async def uploadpic(self, picpath):
        '''上传图片，返回网址'''
        if self.sdkParams == None:
            await self.getRequestKey()
        url = 'https://graph.baidu.com/upload?uptime='+str(time.time())
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
                   'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundary9z1M4HX8R3wt8diF'}
        multipart_encoder = MultipartEncoder(
            fields={
                'image': (os.path.basename(picpath), open(picpath, 'rb')),
                'tn': 'pc',
                'from': 'pc',
                'image_source': 'PC_UPLOAD_FILE',
                'sdkParams': self.sdkParams
            },
            boundary='----WebKitFormBoundary9z1M4HX8R3wt8diF'
        )
        ret = await mypost(url, data=multipart_encoder.to_string(), headers=headers)
        dic = json.loads(ret)
        self.sign = dic["data"]["sign"]
        return "https://graph.baidu.com/s?sign=" + self.sign
    
    async def getMoreSizePic(self):
        '''获取更多尺寸图片，没有的话返回空字典'''
        if self.sign == None:
            raise "No sign"
        url = "https://graph.baidu.com/s?sign=" + self.sign + "&f=all"
        ret = await myget(url)
        it = re.finditer("var cardData = (.+?);\n",ret)
        for match in it:
            dic = json.loads(match.group(1))
            if dic["extData"]["template_name"] == "atom/imageSize":
                url = dic["tplData"]["moreSizeUrl"]
                break
        else:
            return {}
        ret = await myget(url)
        searchresult = re.search('ajaxUrl.:.(.+?)"',ret,re.M|re.I)
        if searchresult:
            url = searchresult.group(1)
        else:
            return {}
        url = url.replace('\\',"")
        ret = await myget(url)
        return json.loads(ret)

    async def getSimilarPic(self, page=1):
        '''获取相似图片'''
        if self.sign == None:
            raise "No sign"
        url = "https://graph.baidu.com/view/similardetailnew?sign=" + self.sign + \
            "&f=refinement&srcp=crs_simi&render_type=json&carousel=1&next=1&tn=wise&idctag=gz&page=" + \
            str(page)
        ret = await myget(url)
        dic = json.loads(ret)
        return dic
