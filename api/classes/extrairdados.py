import requests
from bs4 import BeautifulSoup
import json

class ExtrairDados:

    def __init__(self, url):
        self.url = url

    def __recupera_chave(self) -> str:
        if 'NFCE-COM.aspx?p=' in self.url:
            chave = self.url.split('p=')
            return chave[1]
        if 'NFCE-COM.aspx?' in self.url and 'NFCE-COM.aspx?p=' not in self.url:
            chave = self.url.split('NFCE-COM.aspx?')
            return chave[1]
        return ''

    def __monta_link(self):
        return 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?p=' + self.__recupera_chave()

    def __html_to_json(self,soup, indent=None):
        rows = soup.find_all("tr")
        headers = {}
        thead = soup.find("thead")
        if thead:
            thead = soup.find_all("th")
            for i in range(len(thead)):
                headers[i] = thead[i].text.strip().lower()
        data = []
        for row in rows:
            cells = row.find_all("td")
            if thead:
                items = {}
                if len(cells) > 0:
                    for index in headers:
                        items[headers[index]] = cells[index].text
            else:
                items = []
                for index in cells:
                    items.append(index.text.strip())
            if items:
                data.append(items)
        return json.dumps(data, indent=indent)
    
    def __requisicao(self) -> str:
        headers = {
            "User-Agent":
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        try:
            return requests.get(self.__monta_link(), headers=headers).text
        except Exception as e:
            return ''
        
    def __extrair_tabela(self) -> str:
        try:
            site = BeautifulSoup(self.__requisicao(), "html.parser")
            tabela = site.find_all('table')
            dados = json.loads(self.__html_to_json(tabela[0]))
            conteudo = []
            copiar = False
            for item in dados:
                if 'Valor total' in str(item):
                    copiar = False
                if copiar:
                    conteudo.append(item)
                if "['Código', 'Descrição', 'Qtde', 'Un', 'Vl Unit', 'Vl Total']" == str(item):
                    copiar = True
            return conteudo
        except Exception as e:
            return ''
        
    def extrair(self):
        try:
            produtos = []
            for item in self.__extrair_tabela():
                item = {
                    'produto': item[1],
                    'preco': item[5].replace('.', '').replace(',', '.')
                }
                produtos.append(item)
            #formatado = json.dumps(produtos, indent=2)
            return json.dumps(produtos)
        except:
            return []

if __name__ == '__main__':
    url = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43230993015006001780651050008765821141276787|2|1|1|1BE26B749C734E71F43F4493A87687B02EEC8414'
    print(ExtrairDados(url).extrair())






