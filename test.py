from ImgEngine_client import ImageEngineClient, data2img

client = ImageEngineClient('http://192.168.1.114:9088')
# results = client.search_img(r'E:\z8402\Documents\Python\Test\test_send.jpg')
# message = results[0]['metadata']['message']
# img_data = results[0]['img']
# img = data2img(img_data)
# img.save('test.jpg')
# print(message)
client.read_data('../telegramData/messages.html')
