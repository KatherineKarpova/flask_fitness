import hashlib
print(hasattr(hashlib, "scrypt"))

def main():

    email = "kat@gmail.com"
    email_hash = hashlib.sha256(email.encode()).hexdigest()
    print(email)
    print(email_hash)
    test_hash_func = hash_email(email)
    print(test_hash_func)

def hash_email(email):
    return hashlib.sha256(email.encode()).hexdigest()

if __name__ == "__main__":
    main()