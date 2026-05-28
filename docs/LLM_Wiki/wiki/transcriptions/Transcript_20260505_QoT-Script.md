---
title: "QoT-Script Meeting"
date: 2026-05-05
tags: [transcription, meeting]
status: completed
---

# Meeting Transcript: QoT-Script Meeting (2026-05-05)

**Participants:**
- **Aryanaz Attarpour**
- **Felipe Abadia Bermeo**

**Context:** Weekly thesis meeting.

---

## Transcript

**Aryanaz Attarpour** [0:04]:

> Any desk doesn't work.

> Eight. Sure. Sun. Okay. It's not working in this way.

> You don't know value? That's okay. So maybe I can share it here just a second.

**Felipe Abadia Bermeo** [0:28]:
> Can I?

**Aryanaz Attarpour** [0:29]:

> So that...

**Felipe Abadia Bermeo** [0:30]:

> Can I record the? This.

**Aryanaz Attarpour** [0:35]:

> It's better to not because I'm going to, but I'm always available if you have any questions. So just tell me, okay? I mean, every day or whenever you have a question, just tell me, I'm going to, I can even.

**Felipe Abadia Bermeo** [0:35]:

> Or not. Oh yeah, yeah, yeah, I, I know. Okay.

**Aryanaz Attarpour** [0:54]:

> call you and have a call and we can go through the code. It's okay.

**Felipe Abadia Bermeo** [0:58]:
> Tareef.

**Aryanaz Attarpour** [1:00]:

> Um, yeah, and let me see. Chen. How was your weekend? Charles.

**Felipe Abadia Bermeo** [1:30]:

> Good. I spent the time with my sister. I also had was working, but Friday I didn't do anything.

**Aryanaz Attarpour** [1:43]:

> I.

> Alright.

**Felipe Abadia Bermeo** [1:44]:

> Sunday, Saturday and Sunday I did some research. I it was like investigating.

**Aryanaz Attarpour** [1:49]:

> And just. Okay.

> Okay, I mean, usually on the weekend, you should not work. So, yeah.

**Felipe Abadia Bermeo** [2:00]:

> No, well, it's...

**Aryanaz Attarpour** [2:02]:

> This is the, I'm not a fan of working on the weekends, to be honest, and I thank you. We can do something for us, but sometimes.

**Felipe Abadia Bermeo** [2:14]:

> Yeah, yeah, I understand.

**Aryanaz Attarpour** [2:15]:

> I need to work and I don't like to work on weekends, you know.

**Felipe Abadia Bermeo** [2:19]:
> Yeah.

**Aryanaz Attarpour** [2:22]:

> Yeah, because of that, I'm not very.

> I think people should not work on the weekends, so the whole.

**Felipe Abadia Bermeo** [2:31]:

> I think the same. I think the same. I don't know why there are people that are work addicted, workaholic, you know, and they, no, I don't know how they do because I need the rest. I need some vacations or something. I want to go to a cruise.

**Aryanaz Attarpour** [2:33]:

> Yeah, yeah. Yeah, work on. Show.

> W.

**Felipe Abadia Bermeo** [2:50]:

> Cruiser, Cruise.

**Aryanaz Attarpour** [2:52]:
> Okay.

**Felipe Abadia Bermeo** [2:53]:

> I would like, because I will, I am, I have never been.

**Aryanaz Attarpour** [2:55]:
> And.

**Felipe Abadia Bermeo** [2:58]:

> It would be nice that that that are good vacations.

**Aryanaz Attarpour** [2:58]:

> Mm.

> Yeah, OK, so I managed to... Uh, I managed to, uh... So, can you see my screen?

**Felipe Abadia Bermeo** [3:19]:

> Yeah, I can see it.

**Aryanaz Attarpour** [3:20]:

> Okay, so this is the code. These are these three node test and 12 underline node dot that. They are actually the that files that we use them in a common. They are giving us the topology. So if we look inside, you see that it has the number of the nodes, the unit fibers,

> traffics and a set of candidate locations. So all of them are given or the input of the problem.

**Felipe Abadia Bermeo** [3:47]:
> Mmh.

**Aryanaz Attarpour** [3:51]:

> Um...

**Felipe Abadia Bermeo** [3:51]:

> Okay, so this is those are like the test better, right? Or okay.

**Aryanaz Attarpour** [3:56]:

> Yes, yes, yes, but virtually, you know, it's a virtual, yeah, yeah, yeah, hard coded,

> exactly. So that I consider that I have a three node network, which these three nodes are connected together by a fibers. These fibers are bidirectional, meaning that we have connection from one to two and two to one.

**Felipe Abadia Bermeo** [3:59]:
> Yeah, yeah, yeah, hard-coded. Mhm.

**Aryanaz Attarpour** [4:17]:

> So we call this bidirectional. And I have a set of requests inside the network, which we assume, for example, from node one to node two, 100 G. From node one to node two, another 100 G, and from node two to node three, 100. So these are the traffic requests.

**Felipe Abadia Bermeo** [4:34]:
> Okay.

**Aryanaz Attarpour** [4:37]:

> The other things are not really important, so this is just the source, destination, and... Which rate, and these are the.

> optical amplifier locations that we can put. We don't care about them. Okay, so these are just. Okay. So none of them, these classes, you should not look at them.

**Felipe Abadia Bermeo** [4:54]:
> OK. Okay.

**Aryanaz Attarpour** [5:05]:
> We just need to go to the network that's CPP.

**Felipe Abadia Bermeo** [5:08]:
> Network of Pain.

**Aryanaz Attarpour** [5:11]:

> So we are going to the network that CPP and we need to go, so here I need to.

> Check, let me, it was very null, okay. So what we are going to do here, so we have a function called get paths. This get paths actually calculates the paths.

**Felipe Abadia Bermeo** [5:35]:
> Huh?

**Aryanaz Attarpour** [5:39]:

> Inside the network.

> Okay, you should not look at it because it's based on some OTN boards. Okay.

**Felipe Abadia Bermeo** [5:42]:

> Okay.

> But what do you mean with calculate it?

**Aryanaz Attarpour** [5:49]:

> It's like a shortest path, like shortest path or Dijkstra among the graph, the graph that you have. So we consider the topology, the tree node topology, and a tree node graph with edges, and we calculate the shortest paths for traffic requests.

**Felipe Abadia Bermeo** [5:51]:

> Okay. Yeah.

**Aryanaz Attarpour** [6:09]:
> So, but.

**Felipe Abadia Bermeo** [6:09]:
> Between 2 given nodes, right?

**Aryanaz Attarpour** [6:12]:

> Yes.

> nodes are given, links are given, connection requests are given, and just we need to calculate the paths, possible paths to route the connection requests inside the network. This get packs is a very complicated get pack. So because it is based on some

**Felipe Abadia Bermeo** [6:20]:

> Okay. OK.

**Aryanaz Attarpour** [6:35]:

> OTM boards and grooming, you just do not need to consider them at all.

**Felipe Abadia Bermeo** [6:41]:

> Yes, I understand.

**Aryanaz Attarpour** [6:42]:

> Okay, so just don't look at it.

> So the main part that you need to look at it is get baseline population function. Okay. So we need to go to the definition. Okay, so this, it is all of them are inside the network that CPP. So what we are doing here, it's just the QOT awareness that I mentioned to you previously. So here we...

**Felipe Abadia Bermeo** [7:14]:

> Okay.

**Aryanaz Attarpour** [7:17]:

> Um...

> Put some.

> We calculate some physical layer stuff, like filterless WSS, which again, you do not need to consider them.

**Felipe Abadia Bermeo** [7:32]:

> Mhm.

**Aryanaz Attarpour** [7:35]:

> Okay, so what we are going to do first, let me tell you what is the baseline. So. Wait a second. Okay.

> Oh, okay. This one was not very useful for you. This one I made a mistake. This is the create SNR Aware Minutian oil placement.

**Felipe Abadia Bermeo** [7:58]:

> Okay.

**Aryanaz Attarpour** [7:58]:

> So this function is the main function in your case. So what does this function do? This function goes to this file, which is here, OAGA INFpolimiit underline V3.

**Felipe Abadia Bermeo** [8:11]:
> Yeah.

**Aryanaz Attarpour** [8:12]:

> Okay, so here we have a set of numbers. So these are the candidate location of optical amplifier. So you know here. Okay, so we had these candidate locations in the input file.

**Felipe Abadia Bermeo** [8:28]:
> Yeah.

**Aryanaz Attarpour** [8:30]:

> Okay, so for example, here it says 089. It means that we considered optical amplifier number 0, we considered optical amplifier number 8. So these are the IDs.

**Felipe Abadia Bermeo** [8:42]:
> Eight.

**Aryanaz Attarpour** [8:46]:

> This is the link, this is the kilometer that we put the optical amplifier, and the others we don't, we do not share.

**Felipe Abadia Bermeo** [8:55]:

> Okay.

**Aryanaz Attarpour** [8:56]:

> Okay.

> So here it says that, okay, this is my baseline optical amplifier, meaning that I have this optical amplifier deployed in my network.

**Felipe Abadia Bermeo** [9:08]:
> Mhm.

**Aryanaz Attarpour** [9:09]:
> OK, I have it. OK, now.

**Felipe Abadia Bermeo** [9:11]:
> Yeah.

**Aryanaz Attarpour** [9:14]:

> I need to place it. So, okay, I need to place it. So it goes and reads these numbers to cast to place the optical amplifiers in the simulator. Okay, so it is just doing this here.

**Felipe Abadia Bermeo** [9:27]:
> Yeah.

**Aryanaz Attarpour** [9:34]:

> Yes, this is just this. Okay, so it just reads the optical amplifier and does this. Okay, it should be...

**Felipe Abadia Bermeo** [9:37]:
> Okay.

**Aryanaz Attarpour** [9:46]:

> It's a long time that I didn't work with this code, so...

> S.

> Search, that's it.

> Okay. Yeah, these are reading. It sucks.

> Just.

> Okay, now we come back to the get baseline solution. So these are some physical layer parameters that it's going to check. For example, these are the some losses.

> Okay, so let me go into the detail. Otherwise, it's hard. So what is the filter less? So inside the optical network, we have some switches that these switches let us to

> change the vape length. Okay. Sometimes we do not have this. Sometimes we do not have these switches. Sorry, just a second.

> Sorry.

> So sometimes we do not have these switches, which we call them filterless. Okay? Here, when you say it says, okay, filterless, these are the things that I'm telling you just because...

**Felipe Abadia Bermeo** [10:55]:
> Okay.

**Aryanaz Attarpour** [11:05]:

> You have a better view of what are these things means. Otherwise, it's not important things.

**Felipe Abadia Bermeo** [11:09]:
> Yeah, yeah, yeah.

**Aryanaz Attarpour** [11:13]:

> Um...

> So here filterless is false. When it is false, it means that we do not consider for the as a propagation. What is as a propagation? When you consider the optical amplifiers inside the network, you know that the signal goes to the amplifier and signal is going to be

> somehow amplified. Okay, but this amplifier produces a noise, a type of a noise, which these noise is also amplified.

**Felipe Abadia Bermeo** [11:37]:

> Yeah. Yeah.

**Aryanaz Attarpour** [11:47]:

> Okay, so this noise is called as annoying.

**Felipe Abadia Bermeo** [11:51]:
> It's called Hao.

**Aryanaz Attarpour** [11:52]:
> As the ASE.

**Felipe Abadia Bermeo** [11:54]:
> Hey, I'll get in there that day.

**Aryanaz Attarpour** [11:56]:

> It's as a noise. So this is bad for the network because when it is amplified a lot, it distorts your signal because you have a lot of noise and a very tiny signal, so you cannot

**Felipe Abadia Bermeo** [12:07]:
> Yeah.

**Aryanaz Attarpour** [12:14]:

> It's not good for the network. When we consider it here, when we say filter, this is true, it means that we consider it as a noise. If it is false, we consider it. We do not consider it as a noise. For now, you can skip the as a noise. There is no need.

**Felipe Abadia Bermeo** [12:15]:
> Yes, I understand. OK. Tareef.

**Aryanaz Attarpour** [12:32]:
> For considering it at this moment, OK?

**Felipe Abadia Bermeo** [12:35]:
> OK.

**Aryanaz Attarpour** [12:37]:

> So these are also some physical layer topics like the degree of the node and how you calculate it. To be honest, I myself do not know how we can calculate these stuffs. So I just copy paste it directly from another code.

**Felipe Abadia Bermeo** [12:50]:
> Yeah.

> That's how we do, that's how it works.

**Aryanaz Attarpour** [12:57]:

> Yes, I mean, it works, so, yes.

> And yeah, these are the losses. So for example, here it says that if you have the, if you have the WSS, then you need to consider the filter loss. And these are all of them are mentioned in the network that

> So most of them are defined here.

> You see, for example, Sebastián, Beta, they are just a number.

**Felipe Abadia Bermeo** [13:32]:
> Yeah. Yeah.

**Aryanaz Attarpour** [13:34]:
> For example, field told us DB is 6.

**Felipe Abadia Bermeo** [13:38]:
> Yes, OK.

**Aryanaz Attarpour** [13:38]:

> Okay, so for example, when we mention here that, okay, the loss is filter loss DB, it means it is six.

**Felipe Abadia Bermeo** [13:44]:
> Yes.

**Aryanaz Attarpour** [13:45]:

> So I just want to be a little bit fancy, so I wrote it like this. And this code was written

> in the time that there were no chat GPT and these stuff. And consider that I'm not a computer science guy, so.

**Felipe Abadia Bermeo** [13:50]:

> Yeah, yeah, it's fine.

> Yeah, you know, it's good, it's very good.

**Aryanaz Attarpour** [14:05]:

> Please don't judge my colleague. And these things are actually not related to your topic because these are talking about the genetic algorithm, like the chromosome structure and these things. It is not important.

**Felipe Abadia Bermeo** [14:07]:

> No, no, don't worry.

> Mm-hmm.

**Aryanaz Attarpour** [14:24]:

> The main thing is that you need to create a SNR.

> OA placement, which was actually this one.

> So let me tell you how you need to do it. OK, we have a light path. OK, this light path needs to be checked from the.

**Felipe Abadia Bermeo** [14:41]:
> Okay.

**Aryanaz Attarpour** [14:56]:

> from two points. The first point is power at the receiver side and the other one is SNR. Okay. How we do it? It's like this. SNR threshold.

**Felipe Abadia Bermeo** [15:03]:

> Yes.

**Aryanaz Attarpour** [15:12]:

> So let me just don't give you a lot of not relevant information, just directly going to the what we have to do. So here in the function, yes, it's here. So the main physical

> layer is from here, it's here.

> Get all a lock.

> OK, this is going to use a genetic algorithm. The parts related to genetic algorithms must be...

**Felipe Abadia Bermeo** [15:35]:
> Mhm.

**Aryanaz Attarpour** [15:43]:

> removed totally. Okay. So here you can see that it says it places the optical amplifier and power shapers using genetic algorithm. We do not consider power shapers. We just consider optical amplifiers. Which optical amplifiers? The optical amplifiers that already be mentioned in OA underline GA INFpolimiit V3.

**Felipe Abadia Bermeo** [15:58]:
> Okay. Yeah.

**Aryanaz Attarpour** [16:05]:

> So, we are going to consider that.

> And these are the other related to the genetic algorithm. So what you need is...

> So these are, you can see this pop size is a population size for the genetic algorithm. It is not relevant. This is the chromosome structure, not relevant. What is relevant is Calculate, there is a function.

> I'll calculate demand SNR. Okay, calculate demand, assistenza, here. Okay, this is the main function that calculates the SNR of the light path for you. So this is the main thing that you need to amplify.

**Felipe Abadia Bermeo** [16:53]:
> Okay.

**Aryanaz Attarpour** [17:00]:
> Sorry, you need to implement, OK?

**Felipe Abadia Bermeo** [17:02]:
> Yeah.

**Aryanaz Attarpour** [17:04]:

> So it has a set of candidate paths, the shortest path, this is a case shortest path here. It calls this function as an input, it gets the SNR, which...

> It's a file, you can track it to see. I don't remember what was exactly here, but yes, and then here it checks, it does some calculations and then checks if the SNR demand is more than the defined threshold.

> and the power at the receiver side is more than minus dp, minus 18 dp then.

> It's okay. Otherwise, it's not okay otherwise. Okay, so the main thing that you need to follow is here in get OA lock underline GA. But consider that the GA, we do not care about it.

**Felipe Abadia Bermeo** [17:48]:

> It's OK.

> Okay.

**Aryanaz Attarpour** [18:06]:

> Okay, then this is the calculate demand SNR function that I talked about it. So this is the main, the other main function, calculate demand SNR. So if you want to write the name, this is the main thing that calculates the demand SNR. So you see that there are some physical layer stuff you can.

> copy paste them. No need to, because you know, for example, current power DPM, these things are actually not very related to us.

> So this is having a store on the links that demand use. So for example, when you go from node one to node two, which fibers did you use?

**Felipe Abadia Bermeo** [18:52]:

> Okay.

**Aryanaz Attarpour** [18:53]:

> So for an example, I used only fiber one to two. So it is a four on the number of the fibers that you used for rotating the patch. Then again, here, there are some

> calculations. They're just the calculations. And

> At the end?

> It should return, we see that it's kind of a big function, unfortunately. Okay, in the end, it returns the SNR and power, the two things that we need.

**Felipe Abadia Bermeo** [19:32]:
> Yes.

**Aryanaz Attarpour** [19:32]:

> Okay, SNR and power. So for each demand that you have in the network, for example,

> I have node one and node two and node three. I have a connection request from

> node one to node three. Okay, I need to check. Okay, if I go from node one to node three with the optical amplifiers that I have in this file, is it possible?

**Felipe Abadia Bermeo** [20:09]:
> Okay.

**Aryanaz Attarpour** [20:10]:

> Or not visible, OK?

**Felipe Abadia Bermeo** [20:11]:

> So it will be feasible if the SNR is above the SNR threshold and the power variable is more than minus 18 degrees, right?

**Aryanaz Attarpour** [20:16]:
> Exactly.

> Exactly, exactly. So, how I need to check Kitty?

**Felipe Abadia Bermeo** [20:26]:

> So, the output, the output is basically just feasible, not feasible.

**Aryanaz Attarpour** [20:32]:

> Exactly.

**Felipe Abadia Bermeo** [20:33]:

> And the input is the the input is the are the amplifier topologies and the like the network the current state of the network or.

**Aryanaz Attarpour** [20:40]:

> Yes.

> Exactly, the inputs are nodes, links, Uh, Patti?

**Felipe Abadia Bermeo** [20:55]:

> But.

**Aryanaz Attarpour** [20:55]:

> that you, yeah, paths that you wrote the connection request to them. What are the paths? Paths are the links that you used.

**Felipe Abadia Bermeo** [21:04]:

> Mhm.

**Aryanaz Attarpour** [21:05]:

> to route the demand from node one to node two. Okay, which fiber I use, which edge I used.

**Felipe Abadia Bermeo** [21:14]:

> Yeah.

**Aryanaz Attarpour** [21:14]:

> Okay.

> So, these are the paths which you can use a K-shortest path algorithm for it to calculate it. And the...

> optical amplifiers of the network. So these are the four inputs.

> So, notes, links, demands.

> I forgot to say that traffic requests or demands, yeah, that are the traffic requests or demands, and optical amplifiers.

**Felipe Abadia Bermeo** [21:38]:

> Events.

> Okay. Yes, at an optical.

**Aryanaz Attarpour** [21:51]:
> Okay.

**Felipe Abadia Bermeo** [21:51]:
> Perfect.

**Aryanaz Attarpour** [21:53]:

> And then how I need to check it. So the main, let me tell you, what is the main function? This is calculate demand SNR.

**Felipe Abadia Bermeo** [22:06]:

> Ehsan.

**Aryanaz Attarpour** [22:07]:

> Okay, and the checks of this calculate demand SNR is in the getaway lock underline GA function.

**Felipe Abadia Bermeo** [22:16]:

> Get.

> Good, I will write it, good.

**Aryanaz Attarpour** [22:19]:

> Yeah.

> OK, so this is this should be enough, just this this function, calculate demand, and of course there are other functions inside it which are also related to the physical layers stuff, but they, I think there should be something. What is that?

> function do, it actually places the optical amplifiers that we have in this OAGA in it underlying V3.

**Felipe Abadia Bermeo** [22:48]:
> Mhm.

**Aryanaz Attarpour** [22:49]:

> the optical amplifiers that put and checks if does that calculation regarding the SNR and the power at the receiver side and says, okay, is it feasible or it is infeasible? It's just this.

**Felipe Abadia Bermeo** [23:04]:
> Okay, understood.

**Aryanaz Attarpour** [23:05]:

> Okay, so just take a look at this function. The other things are irrelevant. Okay, maybe I said that the other two functions in the beginning, they are irrelevant. They are the main is here. I'm sorry, it's a long time that I haven't worked with this code. So

**Felipe Abadia Bermeo** [23:13]:

> Okay. Yeah.

> Okay, because I am planning to feed this tool like this, this tool as a kind of a black box.

**Aryanaz Attarpour** [23:26]:
> Ahmad.

**Felipe Abadia Bermeo** [23:36]:

> So, my my system is only going to call this tool and get the result.

**Aryanaz Attarpour** [23:37]:

> And. Okay. Okay.

**Felipe Abadia Bermeo** [23:44]:

> But I have to check how to integrate it with Python, because this is C, right? So I will check.

**Aryanaz Attarpour** [23:50]:

> Is.

> Yeah, this is the last one. Okay. Okay. Maybe there are some wrappers, Python wrappers that we can use.

**Felipe Abadia Bermeo** [24:01]:

> Yeah, I will.

**Aryanaz Attarpour** [24:01]:

> I mean, you know these things better than me because you are a computer science. Yeah. But if you need help, just please let me know. And about the thresholds, we define the thresholds here. So you see that these

**Felipe Abadia Bermeo** [24:05]:

> I...

> Okay, okay, I'll let you know.

**Aryanaz Attarpour** [24:21]:

> values that I mentioned, these variables are here, which we are going to use them in the calculate demand SNR. So if you need them, they are in the header file. SNR thresholds are these.

**Felipe Abadia Bermeo** [24:28]:

> Yeah, okay. Earth.

**Aryanaz Attarpour** [24:36]:

> history. It is not this one. Okay, so there is one SNR, no, not this one. It is the ones that has a 10G, 100G and 200G.

**Felipe Abadia Bermeo** [24:40]:
> Okay. Okay.

**Aryanaz Attarpour** [24:48]:
> So these are the threshold, like 12.2, 8.6, 15.2. You can change them if you want.

**Felipe Abadia Bermeo** [24:55]:
> Yeah, you understood. **Aryanaz Attarpour** 24:57 Okay. **Felipe Abadia Bermeo** 24:59 OK, Aryanaz, thank you so much.

**Aryanaz Attarpour** [24:59]:
> Yes.

> Okay, you're welcome. Just take a look at it and then let me know if you have further questions.

> **Felipe Abadia Bermeo** stopped transcription


