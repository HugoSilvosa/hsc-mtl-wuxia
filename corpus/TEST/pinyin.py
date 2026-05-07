import re
import argparse

PINYIN_SYLLABLES = set("""
a ai an ang ao ba bai ban bang bao bei ben beng bi bian biao bie bin bing bo bu
ca cai can cang cao ce cen ceng cha chai chan chang chao che chen cheng chi chong chou
chu chua chuai chuan chuang chui chun chuo ci cong cou cu cuan cui cun cuo
da dai dan dang dao de dei den deng di dia dian diao die ding diu dong dou
du duan dui dun duo e en er
fa fan fang fei fen feng fo fou fu
ga gai gan gang gao ge gei gen geng gong gou gu gua guai guan guang gui gun guo
ha hai han hang hao he hei hen heng hong hou hu hua huai huan huang hui hun huo
ji jia jian jiang jiao jie jin jing jiong jiu ju juan jue jun
ka kai kan kang kao ke ken keng kong kou ku kua kuai kuan kuang kui kun kuo
la lai lan lang lao le lei leng li lia lian liang liao lie lin ling liu lo long
lou lu luan lue lun luo
ma mai man mang mao me mei men meng mi mian miao mie min ming miu mo mou mu
na nai nan nang nao ne nei nen neng ni nian niang niao nie nin ning niu nong
nou nu nuan nue nuo
o ou
pa pai pan pang pao pei pen peng pi pian piao pie pin ping po pou pu
qi qia qian qiang qiao qie qin qing qiong qiu qu quan que qun
ran rang rao re ren reng ri rong rou ru rua ruan rui run ruo
sa sai san sang sao se sen seng sha shai shan shang shao she shen sheng shi
shou shu shua shuai shuan shuang shui shun shuo si song sou su suan sui sun
suo ta tai tan tang tao te teng ti tian tiao tie ting tong tou tu tuan tui tun
tuo wa wai wan wang wei wen weng wo wu xi xia xian xiang xiao xie xin
xing xiong xiu xu xuan xue xun ya yan yang yao ye yi yin ying yo yong you yu
yuan yue yun za zai zan zang zao ze zei zen zeng zha zhai zhan zhang zhao
zhe zhen zheng zhi zhong zhou zhu zhua zhuai zhuan zhuang zhui zhun zhuo zi
zong zou zu zuan zui zun zuo
""".split())

# Regex para encontrar texto entre [ ... ] o ( ... )
BRACKET_PAREN_PATTERN = re.compile(r'(\[([^\[\]]+)\]|\(([^\(\)]+)\))')

# Verifica si el contenido es solo pinyin, permitiendo mayúsculas
def es_puro_pinyin(texto: str) -> bool:
    palabras = texto.strip().split()
    return all(p.lower() in PINYIN_SYLLABLES for p in palabras)

# Limpia la línea, eliminando bloques pinyin 
def limpiar_linea(linea: str, estadisticas: dict) -> str:
    def reemplazo(match: re.Match) -> str:
        contenido = match.group(2) or match.group(3)
        if es_puro_pinyin(contenido):
            estadisticas['bloques_eliminados'] += 1
            if len(estadisticas['ejemplos']) < 10000000:
                estadisticas['ejemplos'].append(contenido)
            return ''
        return match.group(0)
    return BRACKET_PAREN_PATTERN.sub(reemplazo, linea)

# Procesa el archivo 
def procesar_archivo(ruta_entrada: str, ruta_salida: str):
    estadisticas = {
        'lineas': 0,
        'bloques_eliminados': 0,
        'ejemplos': []
    }

    with open(ruta_entrada, 'r', encoding='utf-8') as f_in, \
         open(ruta_salida, 'w', encoding='utf-8') as f_out:
        for linea in f_in:
            estadisticas['lineas'] += 1
            nueva = limpiar_linea(linea, estadisticas)
            f_out.write(nueva)

    print("\n✅ Procesamiento completado.")
    print(f"📄 Líneas procesadas: {estadisticas['lineas']}")
    print(f"🗑️  Bloques pinyin eliminados: {estadisticas['bloques_eliminados']}")
    if estadisticas['ejemplos']:
        print("🔍 Ejemplos de pinyin eliminados:")
        for ej in estadisticas['ejemplos']:
            print(f"  - {ej}")

if __name__ == '__main__':

    procesar_archivo("test.txt", "testt.txt")
