import logging
import re
from .tokens import Token, TagToken
from .settings import SENTENCE_TAG


def format_telephonenumbers(text: str) -> str:
    """To prevent align problems at later stages, already here convert numbers in the format
    \d\d\d \d\d\d\d to a format with a hyphen, e.g. 557 1234 -> 557-1234
    Otherwise the normalizer will perform this change, causing later alignment processes to break."""
    telephone_formatted = re.sub(r'(\d{3}) (\d{4}[,.?:]?)','\g<1>-\g<2>', text)
    return telephone_formatted


def init_tokens(text: str) -> list:
    tokens_list = []
    running_char_ind = 0
    edited = format_telephonenumbers(text)
    for tok in edited.split():
        if not tok:
            continue
        base_token = Token(tok.strip())
        base_token.set_index(len(tokens_list))
        base_token.set_span(running_char_ind, running_char_ind + len(tok))
        running_char_ind += len(tok) + 1 #count for space after current token
        tokens_list.append(base_token)

    return tokens_list


def extract_text(token_list: list, ignore_tags=True, word_separator='') -> str:
    token_strings = []
    for elem in token_list:
        if isinstance(elem, TagToken) and ignore_tags:
            continue
        if not elem.name:
            continue
        token_strings.append(elem.name)
    if word_separator:
        return f' {word_separator} '.join(token_strings)
    else:
        return ' '.join(token_strings)


def extract_tokenized_text(token_list: list, ignore_tags=True, word_separator='') -> str:
    token_strings = []
    for elem in token_list:
        if isinstance(elem, TagToken) and ignore_tags:
            continue
        if not elem.tokenized:
            continue
        token_strings.append(' '.join(elem.tokenized))
    if word_separator:
        return f' {word_separator} '.join(token_strings)
    else:
        return ' '.join(token_strings)


def extract_clean_text(token_list: list, ignore_tags=True, word_separator='') -> str:
    token_strings = []
    for elem in token_list:
        if isinstance(elem, TagToken) and ignore_tags:
            continue
        if isinstance(elem, TagToken):
            token_strings.append(elem.name)
            continue
        if not elem.clean:
            continue
        token_strings.append(elem.clean)
    if word_separator:
        return f' {word_separator} '.join(token_strings)
    else:
        return ' '.join(token_strings)


def extract_normalized_text(token_list: list, ignore_tags=True, word_separator='') -> str:
    token_strings = []
    for elem in token_list:
        if isinstance(elem, TagToken) and ignore_tags:
            continue
        if isinstance(elem, TagToken):
            token_strings.append(elem.name)
            #token_strings.append('<sil>')
            continue
        if not elem.normalized:
            continue
        for norm in elem.normalized:
            # TODO: check normalizer: why does it return punctuation?
            if norm.norm_str not in [',', '.', ':', '?', '(', ')', '/', '"']:
                token_strings.append(norm.norm_str)
    if word_separator:
        return f' {word_separator} '.join(token_strings)
    else:
        return ' '.join(token_strings).strip()


def extract_transcribed_text(token_list: list, ignore_tags=True, word_separator='') -> str:
    token_strings = []
    for elem in token_list:
        if isinstance(elem, TagToken) and ignore_tags:
            continue
        if isinstance(elem, TagToken):
            token_strings.append(elem.name)
            continue
        if not elem.transcribed:
            continue
        for transcr in elem.transcribed:
            if transcr:
                token_strings.append(transcr)
    if word_separator:
        return f' {word_separator} '.join(token_strings)
    else:
        return ' '.join(token_strings).strip()


def extract_sentences(token_list: list, ignore_tags=True, word_separator='') -> list:
    """Return a list of sentences as represented in token_list. Even if ignore_tags is set to
    True we check for sentence tags to split the list into sentences."""
    sentences = []
    sent_tokens = []
    for elem in token_list:
        if isinstance(elem, TagToken) and elem.name == SENTENCE_TAG:
            if word_separator:
                sent = f' {word_separator} '.join(sent_tokens)
            else:
                sent = ' '.join(sent_tokens)
            sentences.append(sent)
            sent_tokens = []
        elif isinstance(elem, TagToken) and ignore_tags:
            continue
        elif not elem.tokenized:
            continue
        else:
            sent_tokens.extend(elem.tokenized)

    if sent_tokens:
        if word_separator:
            sent = f' {word_separator} '.join(sent_tokens)
        else:
            sent = ' '.join(sent_tokens)
        sentences.append(sent)

    return sentences


def extract_sentences_by_normalized(token_list: list, ignore_tags=True, word_separator='') -> list:
    """Return a list of sentences as represented in token_list. Even if ignore_tags is set to
    True we check for sentence tags to split the list into sentences."""
    sentences = []
    sent_tokens = []
    for elem in token_list:
        if isinstance(elem, TagToken) and elem.name == SENTENCE_TAG:
            if word_separator:
                sent = f' {word_separator} '.join(sent_tokens)
            else:
                sent = ' '.join(sent_tokens)
            sentences.append(sent)
            sent_tokens = []
        elif isinstance(elem, TagToken) and ignore_tags:
            continue
        elif isinstance(elem, TagToken):
            sent_tokens.append(elem.name)
        elif not elem.normalized:
            continue
        else:
            for norm in elem.normalized:
                if norm.norm_str not in [',', '.', ':', '?', '(', ')', '/', '"']:
                    sent_tokens.append(norm.norm_str)

    if sent_tokens:
        if word_separator:
            sent = f' {word_separator} '.join(sent_tokens)
        else:
            sent = ' '.join(sent_tokens)
        sentences.append(sent)

    return sentences


def extract_sentences_by_transcribed(token_list: list, ignore_tags=True, word_separator='') -> list:
    """Return a list of sentences as represented in token_list. Even if ignore_tags is set to
    True we check for sentence tags to split the list into sentences."""
    sentences = []
    sent_tokens = []
    for elem in token_list:
        if isinstance(elem, TagToken) and elem.name == SENTENCE_TAG:
            if word_separator:
                sent = f' {word_separator} '.join(sent_tokens)
            else:
                sent = ' '.join(sent_tokens)
            sentences.append(sent)
            sent_tokens = []
        elif isinstance(elem, TagToken) and ignore_tags:
            continue

        elif isinstance(elem, TagToken):
            sent_tokens.append(elem.name)

        elif not elem.transcribed:
            continue
        else:
            sent_tokens.extend(elem.transcribed)

    if sent_tokens:
        if word_separator:
            sent = f' {word_separator} '.join(sent_tokens)
        else:
            sent = ' '.join(sent_tokens)
        sentences.append(sent)

    return sentences


def extract_tokens_and_tag(token: Token) -> list:
    # if token.name contains space(s), extract each token with the pos
    # e.g. name: 'fimm fimm sjö' pos: 'ta'
    # return: 'fimm ta fimm ta sjö ta'

    results = []

    for tok in token.normalized:
        for elem in tok.norm_str.split():
            results.append(elem)
            results.append(tok.pos)
        if tok.pos == '.':
            results.append('\n')

    return results


def extract_tagged_text(token_list: list, ignore_tags=True) -> str:
    token_strings = []
    for elem in token_list:
        if isinstance(elem, TagToken) and ignore_tags:
            continue
        token_strings.extend(extract_tokens_and_tag(elem))

    return ' '.join(token_strings).strip()


def extract_tokenized_string(sentences: list, sent_split=False) -> str:
    """
    Extract the string from the list of sentences: [[],[], ..., []]
    :param sentences: list of strings
    :return: a string representation of 'sentences'
    """
    tokenized_text = ''
    for sent in sentences:
        if sent_split:
            # replace full stop with sentence-tag
            if sent.endswith('.'):
                sent = sent[:-1]
            tokenized_text += ' ' + sent + ' ' + SENTENCE_TAG
        else:
            tokenized_text += ' ' + sent

    return re.sub('\s+', ' ', tokenized_text).strip()


def align_tokens(clean_token_list: list, tokenized: list, split_sent: bool=False) -> list:
    """Compare token_list to the tokenized string and adjust tokens list if they differ.
    We compare length of token_list to the length of tokenized.split(). If they differ in length
    we compare them tokenwise, and also compare the tokens by length.
    This alignment is necessary since the cleaning is done before the tokenizing.

    :param clean_token_list: a tokenList containing cleaned tokens, but not necessarily correctly tokenized
    :param tokenized: a tokenized version of the tokenList as a list of sentences, tokens separated by a space
    :return a list of cleanTokens, possibly a longer one than the original"""

    clean_str = extract_clean_text(clean_token_list)
    tokenized_string = extract_tokenized_string(tokenized, sent_split=split_sent)
    # make sure we are merging token lists created from the same string
    # remove white spaces and sentence tags, since the tokenizer might have added spaces and the tokenized
    # string might already containe sentence tags
    tmp_tokenized = tokenized_string.replace(SENTENCE_TAG, '.')
    pattern = re.compile(r'[\s.]+')
    if re.sub(pattern, '', clean_str) != re.sub(pattern, '', tmp_tokenized):
        logging.error(clean_str + ' and ' + tokenized_string + ' are not the same, can not merge token lists!')
        raise ValueError('params do not represent the same original string!')

    token_list = tokenized_string.split()
    aligned_list = []
    clean_counter = 0
    tokenized_counter = 0
    # if the token_list containes tags, we need to step back in the enumeration of the clean_token_list
    set_step_back_counter = False
    while clean_counter < len(clean_token_list):
        if set_step_back_counter:
            set_step_back_counter = False
        token = clean_token_list[clean_counter]
        if tokenized_counter >= len(token_list):
            print('tokenized: ' + str(tokenized_counter) + ', cleaned: ' + str(clean_counter) + ' ' + token.name)
        elif isinstance(token, TagToken):
            aligned_list.append(token)
            # tag tokens are not present in token_list, halt the counting for token_list
            tokenized_counter -= 1
        elif not token.clean:
            # clean token is empty, meaning original token was deleted during cleaning
            # repeat comparison with tokenized list in the next round
            token.set_tokenized([])
            aligned_list.append(token)
            tokenized_counter -= 1
        elif token.name == token_list[tokenized_counter]:
            token.set_tokenized([token_list[tokenized_counter]])
            aligned_list.append(token)
        elif token_list[tokenized_counter].startswith('<'):
            tag_token = TagToken(token_list[tokenized_counter], clean_counter)
            aligned_list.append(tag_token)
            # don't we have a 'dot' or some equivalent token in the clean-token-list? or do we need some kind of a flag?
            # let's not step back if the token does not have a clean version, probably some symbol deleted by the cleaner
            if token.name != '.':
                set_step_back_counter = True
                clean_counter -= 1
        else:
            non_splitted_token = token_list[tokenized_counter]
            tokenized_arr = [non_splitted_token]
            next_is_tag = False
            while non_splitted_token != re.sub('\s+', '', token.clean) and tokenized_counter < len(token_list) - 2:
                tokenized_counter += 1
                if token_list[tokenized_counter].startswith('<'):
                    tokenized_counter -= 1
                    token.set_tokenized(tokenized_arr)
                    aligned_list.append(token)
                    next_is_tag = True
                    break
                tokenized_arr.append(token_list[tokenized_counter])
                non_splitted_token = ''.join(tokenized_arr)
            if not next_is_tag:
                token.set_tokenized(tokenized_arr)
                aligned_list.append(token)
                #tokenized_counter -= 1
        clean_counter += 1
        tokenized_counter += 1

    # last closing tag in token_list?
    if tokenized_counter < len(token_list) and token_list[tokenized_counter].startswith('<'):
        tag_token = TagToken(token_list[tokenized_counter], clean_counter)
        aligned_list.append(tag_token)

    return aligned_list
