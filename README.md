# Early (working) version of my STP trainer program

Author: Kamil Kugler

This software is a CLI version of what I was looking for while studying for my CCNA/CCNP exams
and allows you to create different STP topologies, mark port roles and than verify whether you
have it down or still need some more work.

Program will take a json file as an input, proces all of the switches inside of a given STP 802.1D 
domain and subsequently it will produce results as a json file placing it inside of an outputs 
directory. On top of that the program provides a human friendly display as well, that will list 
all important roles and ports on every switch that were assigned to them.

I believe that this kind of software is going to be super usefull for people who are rigorously studying for
CCNA or CCNP, maybe even CCIE in its current form (I suppose in the future as well).

As this program goes I would like it to be used mainly for educational purposes. In case of any 
commercial use I would like to be concacted prior to that and to at least be mentioned as an author :)

I hope that this software (even in its current form) will be of big use to everyone who like me is
studying hard every day and hoping to land a job in what we really love. Or for anyone who wants to 
verify how would the switches behave if you have decided to make some changes that would affect 
connections between them.


All the best !!
Have fun with it:)

p.s. Json files inside of stp_domains directory can be modified according to your needs but at the moment I can not guarantee that everything will always work smoothly.
You might even want to introduce your own topologies if you would like, just follow the same pattern that I have adapted and it shall work just fine for you.
