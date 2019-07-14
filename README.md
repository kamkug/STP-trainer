# STP trainer program

Author: Kamil Kugler

At the moment the software is in early stages in terms of how it has been written.
Although it seems to be working for at least a few of stp_domains that I am including 
inside of the stp_domains directory.

Each file can be selected manually by editing the top of alpha.py and using a name of the file.
I will be working more on this though so do not be discouraged :)

In its current state this program will take a json file as an input, proces all of the
switches inside of a given STP 802.1D domain and subsequently it will produce results as a json file
placing it inside of an outputs directory. On top of that the program provides a human friendly
display as well, that will list all important roles and ports on every switch that were assigned 
to them.

I believe that this kind of software is super usefull for people who are rigorously studying for
CCNA or CCNP, maybe even CCIE in its current form (I suppose in the future as well).

Like with my Subnetting Calculator program I am going to convert this software into a class,
will try to remove a lot of redundancy that currently exists in the code and possibly
might try to create a simple graphical interface as well (although I much prefer working in a CLI).

As this program goes I would like it to be used mainly for educational purposes. In case of any 
commercial use I would like to be concated prior to that and to at least be mentioned as an author :)

I hope that this software (even in its current form) will be of big use to everyone who like me is
studying hard every day and hoping to land a job in what we really love.


All the best !!
Have fun with it:)

p.s. Json files inside of stp_domains directory can be modified according to your needs but at the moment I can not guarantee that everything will always work smoothly (I kinda hope so though hehe).
You might even want to introduce your own topologies if you would like, just follow the same parent
that I have adapted and it shall hopefully work just fine for you.
