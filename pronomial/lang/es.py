import pickle
from os.path import isfile, join, dirname
from nltk.tokenize import word_tokenize
import nltk.tag
import nltk
from string import punctuation
from random import shuffle

PRONOUNS_ES = {
    'male': ['el', "los", 'ello', 'vuestro', 'nuestro', 'este', 'ese',
             'aquel','uno', 'alguno', 'ninguno', 'poco', 'escaso', 'mucho', 
             'demasiado', 'todo', 'otro', 'mismo', 'tanto', 'tan', 'mío',
             'tuyo', 'suyo'],
    'female': ['la', "las", 'ella', 'vuestra', 'nuestra','esta', 'esa',
               'aquella', 'una', 'alguna', 'ninguna', 'poca', 'escasa', 
               'mucha', 'demasiada', 'toda', 'otra', 'misma', 'tanta',
               'alguien', 'nadie', 'cualquiera', 'quienquiera', 'demás',
               'mía', 'tuya', 'suya'],
               'mucha', 'demasiada', 'toda', 'otra', 'misma', 'tanta',
               'alguien', 'nadie', 'cualquiera', 'quienquiera', 'demás',
               'mía', 'tuya', 'suya'],
    'first': ['yo', 'me', 'mí', 'mío', 'conmigo', 'nos', 'míos', 'mías',
    'first': ['yo', 'me', 'mí', 'mío', 'conmigo', 'nos', 'míos', 'mías',
              'nuestro', 'nuestra', 'nosotros'],
    'neutral': ['tú', 'vos', 'usted', 'le', 'se', 'te', 'mí', 'conmigo',
                'esto', 'eso', 'aquello', 'lo', 'cuál', 'cuánto', 'qué', 
                'cómo', 'quién', 'quiénes', 'uno', 'algo', 'nada', 'poco',
                'escaso', 'mucho', 'demasiado', 'todo', 'otro', 'mismo',
                'tanto', 'os', 'que', 'cual', 'quien', 'cuyo', 'donde'],
    'plural': ['nosotras', 'nosotros', 'nuestros', 'nuestras', 'vuestros',
               'vuestras', 'suyo', 'vosotros', 'vosotras', 'ellos', 'ellas',
               'estos', 'esos', 'aquellos','estas', 'esas', 'aquellas', 
               'unos', 'algunos', 'ningunos', 'pocos', 'escasos', 'muchos', 
               'demasiados', 'todos', 'varios', 'otros', 'mismos', 'tantos',
               'unas', 'algunas', 'ningunas', 'pocas', 'escasas', 'muchas', 
               'demasiadas', 'todas', 'varias', 'otras', 'mismas', 'tantas',
               'cualquiera', 'quienquiera', 'demás', 'ustedes', 'mis', 'tus',
               'sus']
}

# special cases, word2gender mappings
GENDERED_WORDS_ES = {
    "female": ['mamá', 'mamás', 'madre', 'madres', 'mujer', 'mujeres', 'tía',
               'tías', 'prima', 'primas', 'chica', 'chicas', 'hermana', 
               'hermanas', 'sobrina', 'sobrinas', 'nieta', 'nietas'],
    "male": ['papá', 'papás', 'padre', 'padres', 'hombre', 'hombres', 'tío',
               'tíos', 'primo', 'primos', 'chico', 'chicos', 'hermano', 
               'hermanos', 'sobrino', 'sobrinos', 'nieto', 'nietos']
} 

# context rules for gender
MALE_DETERMINANTS_ES = ['el', "los", 'ello', 'vosotros', 'nosotros', 'este', 
                        'ese', 'aquel','uno', 'alguno', 'ninguno', 'poco', 
                        'escaso', 'mucho', 'demasiado', 'todo', 'otro', 
                        'mismo', 'tanto', 'tan', 'mío', 'tuyo', 'suyo',
                        ]
FEMALE_DETERMINANTS_ES = ['la', "las", 'ella', 'vosotras', 'nosotras','esta',
                         'esa', 'aquella', 'una', 'alguna', 'ninguna', 'poca',
                         'escasa', 'mucha', 'demasiada', 'toda', 'otra', 
                         'misma', 'tanta', 'alguien', 'nadie', 'cualquiera', 
                         'quienquiera', 'demás', 'mía', 'tuya', 'suya']


def train_es_tagger(path):
    nltk.download('cess_esp')

    def convert_to_universal_tag(t):
        tagdict = {'Fa': '.',
                   'Faa': '.',
                   'Fat': '.',
                   'Fc': '.',
                   'Fd': '.',
                   'Fe': '.',
                   'Fg': '.',
                   'Fh': '.',
                   'Fi': '.',
                   'Fia': '.',
                   'Fit': '.',
                   'Fp': '.',
                   'Fpa': '.',
                   'Fpt': '.',
                   'Fs': '.',
                   'Fx': '.',
                   'Fz': '.',
                   'X': 'X',
                   'Y': 'X',
                   'Zm': 'NUM',
                   'Zp': 'NUM',
                   'ao': 'ADJ',
                   'ao0fp0': 'ADJ',
                   'ao0fs0': 'ADJ',
                   'ao0mp0': 'ADJ',
                   'ao0ms0': 'ADJ',
                   'aq': 'ADJ',
                   'aq00000': 'ADJ',
                   'aq0cn0': 'ADJ',
                   'aq0cp0': 'ADJ',
                   'aq0cs0': 'ADJ',
                   'aq0fp0': 'ADJ',
                   'aq0fpp': 'ADJ',
                   'aq0fs0': 'ADJ',
                   'aq0fsp': 'ADJ',
                   'aq0mp0': 'ADJ',
                   'aq0mpp': 'ADJ',
                   'aq0ms0': 'ADJ',
                   'aq0msp': 'ADJ',
                   'cc': 'CONJ',
                   'cs': 'CONJ',
                   'da': 'DET',
                   'da0fp0': 'DET',
                   'da0fs0': 'DET',
                   'da0mp0': 'DET',
                   'da0ms0': 'DET',
                   'da0ns0': 'DET',
                   'dd': 'DET',
                   'dd0cp0': 'DET',
                   'dd0cs0': 'DET',
                   'dd0fp0': 'DET',
                   'dd0fs0': 'DET',
                   'dd0mp0': 'DET',
                   'dd0ms0': 'DET',
                   'de': 'DET',
                   'de0cn0': 'DET',
                   'di': 'DET',
                   'di0cp0': 'DET',
                   'di0cs0': 'DET',
                   'di0fp0': 'DET',
                   'di0fs0': 'DET',
                   'di0mp0': 'DET',
                   'di0ms0': 'DET',
                   'dn': 'DET',
                   'dn0cp0': 'DET',
                   'dn0cs0': 'DET',
                   'dn0fp0': 'DET',
                   'dn0fs0': 'DET',
                   'dn0mp0': 'DET',
                   'dn0ms0': 'DET',
                   'dp': 'DET',
                   'dp1cps': 'DET',
                   'dp1css': 'DET',
                   'dp1fpp': 'DET',
                   'dp1fsp': 'DET',
                   'dp1mpp': 'DET',
                   'dp1msp': 'DET',
                   'dp1mss': 'DET',
                   'dp2cps': 'DET',
                   'dp2css': 'DET',
                   'dp3cp0': 'DET',
                   'dp3cs0': 'DET',
                   'dp3fs0': 'DET',
                   'dp3mp0': 'DET',
                   'dp3ms0': 'DET',
                   'dt': 'DET',
                   'dt0cn0': 'DET',
                   'dt0fs0': 'DET',
                   'dt0ms0': 'DET',
                   'i': 'X',
                   'nc': 'NOUN',
                   'nc00000': 'NOUN',
                   'nccn000': 'NOUN',
                   'nccp000': 'NOUN',
                   'nccs000': 'NOUN',
                   'ncfn000': 'NOUN',
                   'ncfp000': 'NOUN',
                   'ncfs000': 'NOUN',
                   'ncmn000': 'NOUN',
                   'ncmp000': 'NOUN',
                   'ncms000': 'NOUN',
                   'np': 'NOUN',
                   'np00000': 'NOUN',
                   'np0000a': 'NOUN',
                   'np0000l': 'NOUN',
                   'np0000o': 'NOUN',
                   'np0000p': 'NOUN',
                   'p0': 'PRON',
                   'p0000000': 'PRON',
                   'p010p000': 'PRON',
                   'p010s000': 'PRON',
                   'p020s000': 'PRON',
                   'p0300000': 'PRON',
                   'pd': 'PRON',
                   'pd0cp000': 'PRON',
                   'pd0cs000': 'PRON',
                   'pd0fp000': 'PRON',
                   'pd0fs000': 'PRON',
                   'pd0mp000': 'PRON',
                   'pd0ms000': 'PRON',
                   'pd0ns000': 'PRON',
                   'pe': 'PRON',
                   'pe000000': 'PRON',
                   'pi': 'PRON',
                   'pi0cp000': 'PRON',
                   'pi0cs000': 'PRON',
                   'pi0fp000': 'PRON',
                   'pi0fs000': 'PRON',
                   'pi0mp000': 'PRON',
                   'pi0ms000': 'PRON',
                   'pn': 'PRON',
                   'pn0cp000': 'PRON',
                   'pn0fp000': 'PRON',
                   'pn0fs000': 'PRON',
                   'pn0mp000': 'PRON',
                   'pn0ms000': 'PRON',
                   'pp': 'PRON',
                   'pp1cp000': 'PRON',
                   'pp1cs000': 'PRON',
                   'pp1csn00': 'PRON',
                   'pp1cso00': 'PRON',
                   'pp1mp000': 'PRON',
                   'pp2cp000': 'PRON',
                   'pp2cp00p': 'PRON',
                   'pp2cs000': 'PRON',
                   'pp2cs00p': 'PRON',
                   'pp2csn00': 'PRON',
                   'pp2cso00': 'PRON',
                   'pp3cn000': 'PRON',
                   'pp3cna00': 'PRON',
                   'pp3cno00': 'PRON',
                   'pp3cpa00': 'PRON',
                   'pp3cpd00': 'PRON',
                   'pp3csa00': 'PRON',
                   'pp3csd00': 'PRON',
                   'pp3fp000': 'PRON',
                   'pp3fpa00': 'PRON',
                   'pp3fs000': 'PRON',
                   'pp3fsa00': 'PRON',
                   'pp3mp000': 'PRON',
                   'pp3mpa00': 'PRON',
                   'pp3ms000': 'PRON',
                   'pp3msa00': 'PRON',
                   'pp3ns000': 'PRON',
                   'pr': 'PRON',
                   'pr000000': 'PRON',
                   'pr0cn000': 'PRON',
                   'pr0cp000': 'PRON',
                   'pr0cs000': 'PRON',
                   'pr0fp000': 'PRON',
                   'pr0fs000': 'PRON',
                   'pr0mp000': 'PRON',
                   'pr0ms000': 'PRON',
                   'pt': 'PRON',
                   'pt000000': 'PRON',
                   'pt0cp000': 'PRON',
                   'pt0cs000': 'PRON',
                   'pt0mp000': 'PRON',
                   'pt0ms000': 'PRON',
                   'px': 'PRON',
                   'px1fp0p0': 'PRON',
                   'px1fs0p0': 'PRON',
                   'px1mp0p0': 'PRON',
                   'px1ms0p0': 'PRON',
                   'px2fs0s0': 'PRON',
                   'px3fs000': 'PRON',
                   'px3mp000': 'PRON',
                   'px3ms000': 'PRON',
                   'px3ns000': 'PRON',
                   'rg': 'ADV',
                   'rn': 'ADV',
                   'sn': 'ADP',
                   'sn-SUJ': 'ADP',
                   'sn.co-SUJ': 'ADP',
                   'sn.e': 'ADP',
                   'sn.e-ATR': 'ADP',
                   'sn.e-CD': 'ADP',
                   'sn.e-SUJ': 'ADP',
                   'sn.e.1n-SUJ': 'ADP',
                   'sp': 'ADP',
                   'spcms': 'ADP',
                   'sps00': 'ADP',
                   'va': 'VERB',
                   'vag0000': 'VERB',
                   'vaic1p0': 'VERB',
                   'vaic3p0': 'VERB',
                   'vaic3s0': 'VERB',
                   'vaif1p0': 'VERB',
                   'vaif2s0': 'VERB',
                   'vaif3p0': 'VERB',
                   'vaif3s0': 'VERB',
                   'vaii1p0': 'VERB',
                   'vaii1s0': 'VERB',
                   'vaii2s0': 'VERB',
                   'vaii3p0': 'VERB',
                   'vaii3s0': 'VERB',
                   'vaip1p0': 'VERB',
                   'vaip1s0': 'VERB',
                   'vaip2p0': 'VERB',
                   'vaip2s0': 'VERB',
                   'vaip3p0': 'VERB',
                   'vaip3s0': 'VERB',
                   'vais3s0': 'VERB',
                   'vam02s0': 'VERB',
                   'vam03s0': 'VERB',
                   'van0000': 'VERB',
                   'vap00sm': 'VERB',
                   'vasi1p0': 'VERB',
                   'vasi1s0': 'VERB',
                   'vasi3p0': 'VERB',
                   'vasi3s0': 'VERB',
                   'vasp1s0': 'VERB',
                   'vasp3p0': 'VERB',
                   'vasp3s0': 'VERB',
                   'vm': 'VERB',
                   'vmg0000': 'VERB',
                   'vmic1p0': 'VERB',
                   'vmic1s0': 'VERB',
                   'vmic2s0': 'VERB',
                   'vmic3p0': 'VERB',
                   'vmic3s0': 'VERB',
                   'vmif1p0': 'VERB',
                   'vmif1s0': 'VERB',
                   'vmif2s0': 'VERB',
                   'vmif3p0': 'VERB',
                   'vmif3s0': 'VERB',
                   'vmii1p0': 'VERB',
                   'vmii1s0': 'VERB',
                   'vmii2p0': 'VERB',
                   'vmii2s0': 'VERB',
                   'vmii3p0': 'VERB',
                   'vmii3s0': 'VERB',
                   'vmip1p0': 'VERB',
                   'vmip1s0': 'VERB',
                   'vmip2p0': 'VERB',
                   'vmip2s0': 'VERB',
                   'vmip3p0': 'VERB',
                   'vmip3s0': 'VERB',
                   'vmis1p0': 'VERB',
                   'vmis1s0': 'VERB',
                   'vmis2s0': 'VERB',
                   'vmis3p0': 'VERB',
                   'vmis3s0': 'VERB',
                   'vmm01p0': 'VERB',
                   'vmm02s0': 'VERB',
                   'vmm03p0': 'VERB',
                   'vmm03s0': 'VERB',
                   'vmn0000': 'VERB',
                   'vmp00pf': 'VERB',
                   'vmp00pm': 'VERB',
                   'vmp00sf': 'VERB',
                   'vmp00sm': 'VERB',
                   'vmsi1p0': 'VERB',
                   'vmsi1s0': 'VERB',
                   'vmsi3p0': 'VERB',
                   'vmsi3s0': 'VERB',
                   'vmsp1p0': 'VERB',
                   'vmsp1s0': 'VERB',
                   'vmsp2p0': 'VERB',
                   'vmsp2s0': 'VERB',
                   'vmsp3p0': 'VERB',
                   'vmsp3s0': 'VERB',
                   'vs': 'VERB',
                   'vsg0000': 'VERB',
                   'vsic1s0': 'VERB',
                   'vsic2s0': 'VERB',
                   'vsic3p0': 'VERB',
                   'vsic3s0': 'VERB',
                   'vsif1s0': 'VERB',
                   'vsif3p0': 'VERB',
                   'vsif3s0': 'VERB',
                   'vsii1p0': 'VERB',
                   'vsii1s0': 'VERB',
                   'vsii3p0': 'VERB',
                   'vsii3s0': 'VERB',
                   'vsip1p0': 'VERB',
                   'vsip1s0': 'VERB',
                   'vsip2s0': 'VERB',
                   'vsip3p0': 'VERB',
                   'vsip3s0': 'VERB',
                   'vsis1s0': 'VERB',
                   'vsis3p0': 'VERB',
                   'vsis3s0': 'VERB',
                   'vsm03s0': 'VERB',
                   'vsn0000': 'VERB',
                   'vsp00sm': 'VERB',
                   'vssf3s0': 'VERB',
                   'vssi3p0': 'VERB',
                   'vssi3s0': 'VERB',
                   'vssp1s0': 'VERB',
                   'vssp2s0': 'VERB',
                   'vssp3p0': 'VERB',
                   'vssp3s0': 'VERB',
                   'w': 'NOUN',
                   'z': 'NUM'}
        t = t.lower()
        return tagdict.get(t, "." if all(tt in punctuation for tt in t) else t)

    cess = [[(w, convert_to_universal_tag(t))
             for (w, t) in sent]
            for sent in nltk.corpus.cess_esp.tagged_sents()]
    shuffle(cess)
    def_tagger = nltk.DefaultTagger('NOUN')
    affix_tagger = nltk.AffixTagger(
        cess, backoff=def_tagger
    )
    unitagger = nltk.UnigramTagger(
        cess, backoff=affix_tagger
    )
    tagger = nltk.BigramTagger(
        cess, backoff=unitagger
    )
    tagger = nltk.BrillTaggerTrainer(tagger, nltk.brill.fntbl37())
    tagger = tagger.train(cess, max_rules=100)

    with open(path, "wb") as f:
        pickle.dump(tagger, f)

    return tagger


def load_es_tagger(path=None):
    path = path or join(dirname(dirname(__file__)), "res", "es_tagger.pkl")
    if not isfile(path):
        train_es_tagger(path)
    with open(path, "rb") as f:
        tagger = pickle.load(f)
    return tagger


_POSTAGGER = load_es_tagger()


def pos_tag_es(tokens):
    if isinstance(tokens, str):
        tokens = word_tokenize(tokens)
    return _POSTAGGER.tag(tokens)


# word rules for gender
_FEMALE_ENDINGS_ES = ["a", "as"]
_MALE_ENDINGS_ES = ["o", "os"]


def predict_gender_es(word, text=""):
    # parse gender taking context into account
    word = word.lower()
    words = text.lower().split(" ")
    for idx, w in enumerate(words):
        if w == word and idx != 0:
            # in portuguese usually the previous word (a determinant)
            # assigns gender to the next word
            previous = words[idx - 1].lower()
            if previous in MALE_DETERMINANTS_ES:
                return "male"
            elif previous in FEMALE_DETERMINANTS_ES:
                return "female"

    # get gender using only the individual word
    # see if this word has the gender defined
    if word in GENDERED_WORDS_ES["male"]:
        return "male"
    if word in GENDERED_WORDS_ES["female"]:
        return "female"
    singular = word.rstrip("s")
    if singular in GENDERED_WORDS_ES["male"]:
        return "male"
    if singular in GENDERED_WORDS_ES["male"]:
        return "female"
    # in portuguese the last vowel usually defines the gender of a word
    # the gender of the determinant takes precedence over this rule
    for end_str in _FEMALE_ENDINGS_ES:
        if word.endswith(end_str):
            return "female"
    for end_str in _MALE_ENDINGS_ES:
        if word.endswith(end_str):
            return "male"
    return None
