


'''tukaj pišiva funkcije, ki jih uporabljava'''

#############################################################################
def validate_form(form, required):
    """funkcija ki sprejme formo in vsebine, ki ne smejo biti prazne (required)"""
    messages = []
    for vsebina in required:
        
        value = form.get(vsebina)
        if value is "" or value is None:
            messages.append("%s" % vsebina)
    return messages
#############################################################################

def password_md5(s):
    """Funkcija za hasanje gesel."""
    h = hashlib.md5()
    h.update(s.encode('utf-8'))
    return h.hexdigest()