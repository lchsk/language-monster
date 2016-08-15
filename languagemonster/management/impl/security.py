from functools import wraps
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

def require_superuser(func):
    @wraps(func)
    def _func(*args):
        # args[0] is expect to be a Request object
        if len(args) > 0 and args[0].user.is_superuser:
            return func(*args)
        else:
            return redirect(reverse('index'))
    return _func

def is_superuser(request):
    '''
        Returns True if logged in user is superuser. False otherwise.
    '''

    return (request.user.is_authenticated() and request.user.is_superuser)
    # return render(request, 'app/404.html', c)

def mark_suspicious_words(dataset, words):
    '''
        Analyses each wordpair in adds suspicious=True
        if there are any problems with the wordpair.
    '''

    # import pdb
    # pdb.set_trace()

    # settings

    MAX_WORD_LEN = 12
    UNWANTED_CHARS = '`~!@#$%^&*()-_+=[]{};:\'"?/\\|><.,`'
    CAPITAL_LETTERS = False

    # --

    # dic = {}
    List = []

    for wp in words:

        # dic[wp] = {}
        dic = {}
        dic['wp'] = wp
        dic['susp'] = False
        dic['reason'] = []

        if wp.verified:
            # just keep going
            pass
        else:
            # Check length
            # if len(wp.base) > MAX_WORD_LEN or len(wp.target) > MAX_WORD_LEN:
            #     dic['susp'] = True
            #     dic['reason'].append('Too long (max: {0})'.format(MAX_WORD_LEN))

            # Check for non-alphanumeric characters
            # for c in UNWANTED_CHARS:
            #     if c in wp.base or c in wp.target:
            #         dic['susp'] = True
            #         dic['reason'].append('Unwanted characters present')
            #         break

            # Check for capital letters
            # if CAPITAL_LETTERS:
            #     if wp.base.lower() != wp.base or wp.target.lower() != wp.target:
            #         dic['susp'] = True
            #         dic['reason'].append('Capital letters present')

            en_verification = False

            if dataset.pair.base_language.acronym == 'en':
                if wp.base == wp.target_en:
                    en_verification = True

            if not en_verification:
                dic['susp'] = True
                dic['reason'].append('English verification failed')

        List.append(dic)

    return List
