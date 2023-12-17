from remi import start, App
from remi.gui import Container, Button, FileUploader, FileSelectionDialog, decorate_set_on_listener, decorate_event
import remi.gui as gui
from PyPDF2 import PdfReader
import requests
from libretranslatepy import LibreTranslateAPI
from io import BytesIO
import time
import threading

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
        my_js_head = """
            <script >
            
            console.log('Start');
            $('#pdf_doc').on('load', function(){
        document.write('Start');
        var iframe = $('#pdf_doc').contents();

        iframe.find("#pdf_doc").click(function(){
               alert("test");
               console.log('Click');

        });
});
            </script>""" % {'id':str(id(self)), 'callback_function': 'text_selected'}
        self.page.children['head'].add_child('myjs', my_js_head)
        self.pdf_doc = None

        self.container = gui.VBox(width='100%', height='100%')
        self.text_holder = gui.VBox(width='100%', height='100%')


        self.response_text = TextField()
        self.response_text.set_position(650, 0)
        self.response_text.style['top-margin'] = '10%'
        self.response_text.style['width'] = '45%'
        self.response_text.style['height'] = '45%'
        self.response_text.set_text('Здесь будут результаты вашего запроса')

        self.text_holder.style['display'] = 'flex'
        self.text_holder.style['flex-direction'] = 'row'
        self.container.style['align-items'] = 'center'
  
        self.file_dialog = CorrectSelectionDialog()
        self.file_dialog.style['display'] = 'none'

        self.the_big_text = gui.Widget(_type='iframe', width=290, height=200, margin='10px')
        self.the_big_text.attributes['type'] = 'application/pdf'
        self.the_big_text.style['top'] = '10%'
        self.the_big_text.style['width'] = '45%'
        self.the_big_text.style['height'] = '45%'
        self.the_big_text.attributes['id'] = 'pdf_doc'


        self.open_button = Button('Открыть файл')
        self.open_button.style['x'] = '0px'
        self.open_button.style['y'] = '0px'
        
        self.click_coords = []

        self.menu = ButtonMenu()
        self.menu.style['position'] = 'absolute'
        self.menu.style['z-index'] = '99999999'

        self.text_holder.append(self.the_big_text)
        self.text_holder.append(self.response_text)
        self.container.append(self.text_holder)
        self.container.append(self.menu)
        self.container.append(self.file_dialog)
        self.text_holder.append(self.open_button)

        

        self.text_holder.onmousedown.do(self.mouse_down)
        self.text_holder.onmouseup.do(self.mouse_up)
        self.menu.close_button.onclick.do(self.close)
        self.menu.summarize_button.onclick.do(self.summarize)
        self.menu.paraphraze_button.onclick.do(self.paraphrase)
        self.menu.translate_button.onclick.do(self.translate)
        self.open_button.onclick.do(self.open_file_dialog)
        self.file_dialog.confirm_value.do(self.open_file)
        self.the_big_text.onclick.do(self.test)

        self.current_text = ''
        self.translator = LibreTranslateAPI("https://translate.terraprint.co/")


        return self.container
    
    def test(self):
        print('BBBBBBBBBBBBBBBBBB')

    def open_file_dialog(self, *args):
        self.file_dialog.style['display'] = 'block'

    def open_file(self, *args):
        self.pdf_doc = PdfDocument(args[1][0])
        self.the_big_text.attributes['src'] = self.pdf_doc.path_done
        
    
    def close(self, *args):
        self.menu.style['display'] = 'none'
    
    def mouse_down(self, *args):
        self.click_coords = list(map(lambda x: int(float(x)), args[1:]))

    def mouse_up(self, *args):
        print('AAAAAAA')
        self.execute_javascript("""
                                    var params = {};
                                    params['text'] = window.getSelection().toString();
                                    remi.sendCallbackParam('%(id)s','%(callback_function)s',params)""" % {'id':str(id(self)), 'callback_function': 'text_selected'}) #самое важное
        

    def text_selected(self, **args):   
        if args['text'] != '':
            self.current_text = args['text']
            self.menu.style['left'] = str(self.click_coords[0]) + 'px'
            self.menu.style['top'] = str(self.click_coords[1] - 10) + 'px'
            self.menu.style['display'] = 'block'
            
            
    def summarize(self, *args):
        self.response_text.set_text('Обрабатываем...')
        self.do_gui_update()
        response = requests.post(SUMMARY_URL, headers=HEADERS, json={"inputs": self.current_text})
        self.response_text.set_text(response.json()[0]['summary_text'])
        return 'Ы'
    
    def translate(self, *args):
        self.response_text.set_text('Обрабатываем...')
        self.do_gui_update()
        self.response_text.set_text(self.translator.translate(self.current_text, "en", "ru"))
        return 'Ы'
    
    def paraphrase(self, *args):
        self.response_text.set_text('Обрабатываем...')
        self.do_gui_update()
        response = requests.post(PARAPHRASE_URL, headers=HEADERS, json={"inputs": self.current_text})
        self.response_text.set_text(response.json()[0]['generated_text'])
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


class CorrectSelectionDialog(FileSelectionDialog):
    @decorate_set_on_listener("(self, emitter, fileList)")
    @decorate_event
    def confirm_value(self, widget):
        """event called pressing on OK button.
           propagates the string content of the input field
        """
        self.style['display'] = 'none'
        params = (self.fileFolderNavigator.get_selection_list(),)
        return params
    
    @decorate_set_on_listener("(self,emitter)")
    @decorate_event
    def cancel_dialog(self, emitter):
        """Event generated by the Cancel button click."""
        self.style['display'] = 'none'
        return ()
    
    @decorate_set_on_listener("(self,emitter)")
    @decorate_event
    def confirm_dialog(self, emitter):
        """Event generated by the OK button click.
        """
        
        return ()
    

class PdfDocument(gui.Widget):
    def __init__(self, path, **kwargs):
        super().__init__(**kwargs)
        self._buf = None
        self._buflock = threading.Lock()
        self.path_done = self.get_server_path(path)
        
        
    def get_server_path(self, path):
        with open(path, "rb") as file:
            buf = BytesIO(file.read())

        with self._buflock:
            if self._buf is not None:
                self._buf.close()
            self._buf = buf

        i = int(time.time() * 1e6)
        return "/%s/get_pdf_data?update_index=%d" % (id(self), i)


    def get_pdf_data(self, update_index):
        with self._buflock:
            if self._buf is None:
                return None
            self._buf.seek(0)
            data = self._buf.read()

        return [data, {'Content-type': 'application/pdf'}]

        

# starts the web server
start(MyApp)