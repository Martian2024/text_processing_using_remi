from remi import start, App
from remi.gui import decorate_event_js, decorate_set_on_listener, decorate_event, Container, Button
import remi.gui as gui
from PyPDF2 import PdfReader
import requests
from libretranslatepy import LibreTranslateAPI


SUMMARY_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
TRANSLATION_URL = "https://google-translate1.p.rapidapi.com/language/translate/v2"
PARAPHRASE_URL = "https://api-inference.huggingface.co/models/humarin/chatgpt_paraphraser_on_T5_base"
HEADERS = {"Authorization": "Bearer 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"}
TRANSLATION_HEADERS = {"content-type": "application/x-www-form-urlencoded",
	"Accept-Encoding": "application/gzip",
	"X-RapidAPI-Key": "a38f0247e4msh734f1edcb316305p1412bfjsnbb9bd552f855",
	"X-RapidAPI-Host": "google-translate1.p.rapidapi.com"}


class MyApp(App):
    def __init__(self, *args):
        super(MyApp, self).__init__(*args)
        

    def main(self):
        self.container = gui.VBox(width=700, height=700)
        self.the_big_text = TextField()
        self.the_big_text.set_position(0, 0)
        self.the_big_text.set_size(600, 300)
        self.container.onmousedown.do(self.mouse_down)
        self.container.onmouseup.do(self.mouse_up)
        self.reader = PdfReader('Starbase.pdf') #твой пдф
        self.page_num = 0
        self.the_big_text.set_text(self.reader.pages[0].extract_text()) #пока только 1 страница загружаю
        self.click_coords = []
        self.menu = ButtonMenu()
        self.container.append(self.the_big_text)
        self.container.append(self.menu)
        self.menu.close_button.onclick.do(self.close)
        self.current_text = ''
        self.translator = LibreTranslateAPI("https://translate.terraprint.co/")

        self.menu.summarize_button.onclick.do(self.summarize, 'text')
        self.menu.paraphraze_button.onclick.do(self.paraphrase)
        self.menu.translate_button.onclick.do(self.translate)

        self.menu.style['position'] = 'absolute'

        return self.container

    def close(self, *args):
        self.menu.style['display'] = 'none'
    
    def mouse_down(self, *args):

        self.click_coords = list(map(int, args[1:]))

    def mouse_up(self, *args):
        self.execute_javascript("""
                                    var params = {};
                                    params['text'] = window.getSelection().toString();
                                    remi.sendCallbackParam('%(id)s','%(callback_function)s',params)""" % {'id':str(id(self)), 'callback_function': 'text_selected'}) #самое важное
        

    def text_selected(self, **args):   
        if args['text'] != '' and args['text'] != self.current_text:
            self.current_text = args['text']
            self.menu.style['left'] = str(self.click_coords[0]) + 'px'
            self.menu.style['top'] = str(self.click_coords[1] - 10) + 'px'
            self.menu.style['display'] = 'inline'
            
            
    def summarize(self, *args):
        response = requests.post(SUMMARY_URL, headers=HEADERS, json={"inputs": self.current_text})
        print(response.json()[0]['summary_text'])
        return response.text
    
    def translate(self, *args):
        print(self.translator.translate(self.current_text, "en", "ru"))
        return 'Ы'
    
    def paraphrase(self, *args):
        response = requests.post(PARAPHRASE_URL, headers=HEADERS, json={"inputs": self.current_text})
        print(response.json())
        return 'Ы'


        
        

class TextField(gui.SvgText):
    def __init__(self, *args):
        super().__init__(*args)


class ButtonMenu(Container):
    def __init__(self):
        super().__init__(width=500, height=50)
        self.style['display'] = 'none'
        self.style['left'] = '5px'
        self.style['top'] = '5px'
        self.style['background-color'] = 'FloralWhite'
        self.style['border-radius'] = '10px'
        self.style['border-color'] = 'red'
        self.style['border-width'] = '2px'

        self.close_button = CloseButton()
        self.append(self.close_button)
        self.translate_button = MainButton('Перевести')
        self.append(self.translate_button)
        self.paraphraze_button = MainButton('Перефразировать')
        self.append(self.paraphraze_button)
        self.summarize_button = MainButton('Выжимка')
        self.append(self.summarize_button)


class CloseButton(Button):
    def __init__(self):
        super().__init__(width=30, height=30)
        self.set_text('X')
        self.style['left'] = '400px'
        self.style['top'] = '5px'
        self.style['color'] = 'black'
        self.style['background-color'] = 'red'
        self.style['box-shadow'] = 'none'
        self.style['display'] = 'inline-block'
        self.style['vertical-align'] = 'middle'


class MainButton(Button):
    def __init__(self, text):
        super().__init__(width=120, height=30, text=text)
        self.style['color'] = 'white'
        self.style['background-color'] = 'Aqua'
        self.style['border-radius'] = '10px'
        self.style['box-shadow'] = 'none'
        self.style['display'] = 'inline-block'
        self.style['vertical-align'] = 'middle'
        
        

# starts the web server
start(MyApp)