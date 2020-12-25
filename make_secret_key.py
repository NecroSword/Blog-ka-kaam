import os 

#Session ki secret key banane ke liye
with open('secret_key.txt','wb') as f:
    sk = os.urandom(16)
    f.write(sk)

