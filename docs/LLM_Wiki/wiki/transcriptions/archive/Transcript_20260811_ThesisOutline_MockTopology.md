---
title: "Thesis Outline Feedback & Mock Topology Strategy"
date: 2026-08-11
tags: [transcription, meeting, thesis-outline, mock-topology, german-topology]
status: completed
---

# Meeting Transcript: Thesis Outline Feedback & Mock Topology Strategy (2026-08-11)

**Participants:**
- **Aryanaz Attarpour**
- **Felipe Abadia Bermeo**
- **Qiaolun Zhang**
- **Zheng Zhang**

**Context:** Automatically ingested Teams transcription.

---

## Transcript

**Qiaolun Zhang** [0:03]:

> Well, we introduce why we perform this study, and...

> A...

> Also a little bit backgrounds, it is typically called motivation.

**Felipe Abadia Bermeo** [0:14]:
> Okay.

**Qiaolun Zhang** [0:14]:

> You don't need to have some separate subsections for the motivation, like 1.1 and 1.2. It also makes people feel a little bit about its like background and the related works, but in...

> This is, you don't need to put too much of this part. Let me, wait a second, I can show you another example. Propose solution and contribution.

**Zheng Zhang** [0:53]:
> Okay.

**Qiaolun Zhang** [1:09]:

> Background authentic AI limitations of.

> For this part, I think there is um... Wait a second. Maybe you can call. Call this part overview and motivation, like... Well, you can make 1.3 an overview and motivation. And then we can put the materials you have. Have before inside.

**Felipe Abadia Bermeo** [2:04]:
> Okay, perfect.

**Qiaolun Zhang** [2:05]:
> Overview and motivation. And then, for 0.2, I think... Um...

> What we typically do is that, before the research gap, the previous three sections should be a little bit in parallel, so, and also in terms of the subsection title, it's not very...

> Common to have limitation in the middle.

> So, you should have three subsections in parallel, or two subsections in parallel, but you can comment why some of the previous works are not good enough, but it's not very like inside the subsection, but the subsection title. It's better not to use limitation.

**Felipe Abadia Bermeo** [2:58]:
> OK.

**Qiaolun Zhang** [3:00]:

> And. I think we don't need to have... Oh.

> Very detailed. Subsection title here. Reliance on. Post-deployment retry loops. I think for this part, it is a bit...

> Very concentrated on a specific topic there, like we try to loops. I think maybe we can.

**Felipe Abadia Bermeo** [3:58]:
> Generalize.

**Qiaolun Zhang** [3:58]:

> have a more higher level or like put a bit more summary of what has been done and it could be a sub.

> one component inside this section to talk about in detail what people do when they design the agents for LM. But if you put only retry loops, it makes me feel it's a bit too limited.

> So, 2.1 is a higher level summary of the background, and then you can have some subsections to talk about the details, but not too focused on one specific topic.

**Felipe Abadia Bermeo** [4:44]:
> Yes.

**Qiaolun Zhang** [4:48]:

> OK, system model.

> Okay, like pipeline implementation. Experimental set-top.

> For this part?

> 5.5, we typically do not have a, we will not have a specific section, like a dedicated section for comparison with baselines. Instead, comparison with baseline is involved in all the subsections like 5.3, 5.4.

**Felipe Abadia Bermeo** [5:45]:

> Okay.

**Qiaolun Zhang** [5:53]:

> When we evaluate the metrics, we compare, we put all solutions together.

**Felipe Abadia Bermeo** [5:54]:
> I understand.

**Qiaolun Zhang** [6:00]:

> So, I think...

> This can be deleted, but these metrics can be compared like within the subsection like 5.4 or 5.3.

**Felipe Abadia Bermeo** [6:15]:

> Yes, okay. Good.

**Qiaolun Zhang** [6:27]:

> Yeah, I think for our other subset section type, it's fine. Yeah.

> You can revise it and send me another version, and then I will also, like, check it also, and then I will also write an e-mail to Professor Dora, so that he is aware that we're going to that you are going to graduate in October. because we need to like organize the students and then find the committee members to see where, like which professor to go to which section, which section of defense, yeah.

**Felipe Abadia Bermeo** [6:57]:
> Yes. Okay, yes. Yeah.

**Qiaolun Zhang** [7:14]:
> OK, hi Aryanaz, how are you?

**Felipe Abadia Bermeo** [7:15]:
> Hello, Aryanaz. How are you?

**Aryanaz Attarpour** [7:17]:

> Sorry, fine, thank you. Sorry for the late participation. You know, it is summer and the situation is a bit different. I received your e-mail, Felipe, so I was, I didn't respond on purpose because I was thinking that maybe it is more

**Felipe Abadia Bermeo** [7:21]:
> No, don't worry.

**Qiaolun Zhang** [7:25]:

> Yeah, I know, alright, yeah.

**Aryanaz Attarpour** [7:36]:
> Appropriate that I, you know.

> give answers in the meeting. So do you still, so the main, you mentioned that the missing information is the topology.

**Felipe Abadia Bermeo** [7:43]:
> Okay.

**Aryanaz Attarpour** [7:52]:

> The exact physical fiber span length between the tested nodes, so...

> The fact is that the test bed that we have, it has a very short fiber span lengths.

**Felipe Abadia Bermeo** [8:04]:
> Yeah.

**Aryanaz Attarpour** [8:06]:

> This is also one problem that we previously had. So I suggest to you that you consider just a random number. Like, I don't know that if Qiaolun told you to consider the three node network topology or you're going to consider a more node network.

> Qiaolun, which one you are going to consider as a topology?

**Qiaolun Zhang** [8:29]:

> Felipe, I will consider our topology with a larger number of nodes, but if Mëmëdhe can share some data, then that could also be used for maybe some small tests.

**Aryanaz Attarpour** [8:34]:
> Okay.

> Yeah. And the fact is that the fibers that we have in the test bed, it is not even 1 kilometer. So it is a very short fibers. So this is 1 problem. So for the sake of having a good results and good numerical results, it's better to just consider a bigger network topologies.

**Felipe Abadia Bermeo** [8:45]:
> Because.

**Qiaolun Zhang** [8:50]:
> Okay.

**Felipe Abadia Bermeo** [8:53]:
> Yeah.

**Aryanaz Attarpour** [9:03]:

> like German, like any other Japan topology or anything. And then you can consider the fiber lengths in that topologies. This is, I suggest this for the topology information.

**Qiaolun Zhang** [9:03]:

> Yeah.

**Felipe Abadia Bermeo** [9:18]:
> Thank you. Yes. Okay. Okay. Thank you.

**Aryanaz Attarpour** [9:23]:

> And about your welcome and about the expected operational gains of the deployed EDFAs. So in the simulator that I shared with you in the C format, there is a class called OA lock.

**Felipe Abadia Bermeo** [9:35]:
> Yeah. See, yes.

**Aryanaz Attarpour** [9:45]:

> dot CPP and OA lock dot header. I'm not sure. I think it's in the header part. You can check the gain of the amplifiers there. Again, in, yes, please.

**Felipe Abadia Bermeo** [9:56]:
> It.

**Aryanaz Attarpour** [10:10]:
> I think.

**Felipe Abadia Bermeo** [10:10]:

> The problem, the problem before was that the idea, the original idea, was to get the topology, like build the topology for the system based on the original test bed, so I wanted the API, I thought that the API.

**Aryanaz Attarpour** [10:27]:
> Okay.

**Felipe Abadia Bermeo** [10:31]:

> That connects that I would going to use to connect the system with the test bed had this get endpoint to retrieve directly the physical attributes from the test bed, but it doesn't, so what...

**Aryanaz Attarpour** [10:41]:
> Uh-huh. Yes.

**Felipe Abadia Bermeo** [10:48]:

> We are, we are thinking now to do is not.

> Getting the topology from the original is about mocking the test, but that is precisely what what did you suggest? Yes, and...

**Aryanaz Attarpour** [10:59]:

> Yes, it's very good.

> Yes, I think it's the best option.

**Felipe Abadia Bermeo** [11:05]:

> And we in the future future contributions, like the final section of the document, we

> can say that in the future it can be implemented a way to get the topology from the testbed.

> That that is the idea I had with the the graph, the graph building building a topology for the LLM.

**Aryanaz Attarpour** [11:25]:
> Yes. Yes.

> Yeah, yeah, I think.

**Felipe Abadia Bermeo** [11:34]:

> But for now, we have to mock it.

**Aryanaz Attarpour** [11:36]:

> Yeah, I think if you mock it, you have even a stronger point to make because the test bed that we have, it doesn't even have the ILI amplifiers. While if you mock the topology and you mock everything, then you have a stronger point. Yeah. And then you can say that, okay, so since the test bed doesn't have.

**Felipe Abadia Bermeo** [11:40]:

> Yes, I was.

> Yeah.

> Yeah. I can put it.

**Aryanaz Attarpour** [11:57]:

> this, the situation would be simpler and this approach that I have can be adapted to the testbed later or in the future. Yeah.

**Felipe Abadia Bermeo** [12:07]:

> Exactly, exactly. Yes, I arrived to this to the same conclusion, because the test bed has three nodes and we can, we can, we can do a better simulation with a mock test, but yes, but thank you, thank you Aryanaz, and everything I think everything you need is in the end.

**Qiaolun Zhang** [12:15]:
> Okay.

**Aryanaz Attarpour** [12:22]:
> Yes, of course, of course. You're welcome.

**Felipe Abadia Bermeo** [12:27]:

> In the simulator, I did what I was telling Professor Chen, I did mock the test bed with three nodes, but I can put more nodes and I can put them more like amplifiers, I mean this stuff, but maybe if you can suggest me a topology.

**Aryanaz Attarpour** [12:42]:
> Oops.

**Felipe Abadia Bermeo** [12:47]:

> A number of nodes, the characteristics, and I would receive it.

**Aryanaz Attarpour** [12:54]:

> OK, yes, there is. There is a 17 node German topology that we have, or we can also use the 12 node network topology that I have.

**Felipe Abadia Bermeo** [13:02]:
> Mëmëdhe.

**Aryanaz Attarpour** [13:09]:

> So for the 17 or even the 14 node in Japan topology, I don't know which one Qiaolun prefers because it's also.

**Qiaolun Zhang** [13:22]:

> I think anyone, yeah, any topology is fine. Any real world topology is fine.

**Aryanaz Attarpour** [13:23]:
> Ohh.

> Okay, I think a 17 German is the best one, I mean, because it has a, because it has a very long fibers.

**Qiaolun Zhang** [13:32]:
> What? Why?

**Felipe Abadia Bermeo** [13:32]:
> Okay.

**Qiaolun Zhang** [13:38]:

> You prefer to have a very long fiber? Yeah.

**Aryanaz Attarpour** [13:39]:

> compared to the Japan. Yeah, I prefer this because you can put more optical amplifiers.

**Felipe Abadia Bermeo** [13:47]:

> And I just searched for the 17 node German topology in internet and I have the characteristics, so, okay.

**Aryanaz Attarpour** [13:53]:

> Yes, yes, yes, yes, yes, it is on the, you search on the network and you can see the topology, the fiber lengths and how they are connected.

**Felipe Abadia Bermeo** [14:05]:

> Perfect. Perfect. That is what I mean.

**Aryanaz Attarpour** [14:08]:
> Yeah.

> Okay, so thank you. If you have any further questions, please let me know.

**Felipe Abadia Bermeo** [14:18]:

> Okay, yes, I will if I have.

> Okay, for now, I would also want you to help me with the intents, the set of intents that I, with which we can try.

**Aryanaz Attarpour** [14:21]:

> Okay, thank you.

> At the set of intense, what do you mean by set of intense?

**Felipe Abadia Bermeo** [14:39]:

> the set of intents. Like, what are we going to write it? What is the operator going to write it to in the system? I was thinking maybe...

**Aryanaz Attarpour** [14:52]:
> Okay.

**Felipe Abadia Bermeo** [14:53]:
> And...

> Yeah, like, like connect node, I want to establish a path, a light path between node and node with what characteristics with, I don't know. So I would like different, different kinds of different types of intents with different characteristics to be.

**Aryanaz Attarpour** [14:55]:

> Yeah, yeah, I got it. I got it.

> Yes, of course.

> Okay.

**Felipe Abadia Bermeo** [15:16]:

> To be evaluated, or yeah.

**Aryanaz Attarpour** [15:19]:

> Okay, okay, I definitely can help on this.

> So I will share some examples on how to do it with you. Let me write it, otherwise I report, yeah.

**Felipe Abadia Bermeo** [15:31]:

> Thank you, Aryanaz.

**Aryanaz Attarpour** [15:31]:
> Share the examples. Okay, you're welcome.

**Felipe Abadia Bermeo** [15:40]:

> And the...

> For me, is everything.

> I wanted to show you the system working right now, because I was trying with it some things. But I have some book problems, and it is also kind of slow, so I wanted to optimize it.

> As much as I as I can, and they wanted to ask you about the the Kimiyapi. Does this Kimiyapi can I? I'm not sure, but can I reduce the the thinking process of the LLM? Because I think it is thinking a lot and it's spending.

> So much times in things that it shouldn't, but I have not explored that with the API. I don't know, I don't know.

> Oh.

**Qiaolun Zhang** [16:39]:

> Yeah, I also haven't explored, but another thing that if you, you can also change, I think, the API from V1 to V2, because now you can also maybe V3.

> Let me, uh, because now new version can me uh API can also be used.

> Like, I can also give you some a bit more information later. Let me check. I think for their intelligence.

**Felipe Abadia Bermeo** [17:11]:

> Because...

**Qiaolun Zhang** [17:15]:

> Um...

> I think it can be, it should, it can be changed.

**Felipe Abadia Bermeo** [17:25]:

> Well, I tried to change, like, to...

> Change it in the in the program in the code with Python, like calling when calling the API, but I didn't get different results in terms of time. I have to to see.

**Qiaolun Zhang** [17:42]:
> Ohh.

**Felipe Abadia Bermeo** [17:46]:

> I have to explore the token usage. I didn't try, and maybe I can see that also. But if I could access the website of Kimi with the...

> with some credentials, I don't know, to see in the interface how many tokens am I using or which model it is using in the API. If you have it, it would be nice even though, well, don't worry.

**Qiaolun Zhang** [18:20]:

> Okay, because you also wanted to evaluate the number of tokens you used in your evaluation, right?

**Felipe Abadia Bermeo** [18:28]:

> Yeah.

> Yes, perfect.

**Qiaolun Zhang** [18:30]:

> Okay. K.

> Yeah.

> Let me check.

> Yeah.

> Because we.

> For the one that I provided with you, it's like Kimi coding plan. Even in the platform, it's hard to see. I was also thinking about like maybe we can also have a bit evaluations from one or two other modules. Yeah. I will check this and I will let you know.

**Felipe Abadia Bermeo** [19:17]:

> OK, thank you, Professor. I also wanted to let you know that I am moving again backto-back in Milan.

**Qiaolun Zhang** [19:18]:
> You're welcome.

> Yeah.

**Felipe Abadia Bermeo** [19:27]:
> Air. And...

**Qiaolun Zhang** [19:29]:

> Uh, you travel back to Milan?

**Felipe Abadia Bermeo** [19:31]:
> Yes, I'm going back.

**Qiaolun Zhang** [19:32]:
> Why?

> Not touring is not good enough.

**Felipe Abadia Bermeo** [19:34]:
> And, because...

> No, it is good, but I would like to find a job in Milan. That's that is why, and I hadn't already had an half an apartment, so I am moving the 1st of September.

**Qiaolun Zhang** [19:43]:
> Ahh. OK.

**Felipe Abadia Bermeo** [19:52]:

> That is Tuesday, so...

**Qiaolun Zhang** [19:55]:
> Yeah.

**Felipe Abadia Bermeo** [19:56]:
> So, maybe meeting that Tuesday is difficult.

**Qiaolun Zhang** [20:00]:
> Yeah.

> Yeah, yeah, we can meet in September.

**Felipe Abadia Bermeo** [20:10]:

> Okay, thank you everyone. I don't have anything else to say.

**Qiaolun Zhang** [20:16]:
> Okay, thank you too.

**Felipe Abadia Bermeo** [20:18]:
> Thank you.

**Aryanaz Attarpour** [20:18]:
> Thank you.

**Zheng Zhang** [20:19]:
> Thank you. Thank you.

**Felipe Abadia Bermeo** [20:21]:

> Thank you, Zheng. Thank you, Aryanaz. Thank you very much. And I guess, bye bye. No, no, no, bye bye. I was.

**Aryanaz Attarpour** [20:23]:
> Thank you. Bye-bye. I guess so.

> No, no, sorry, I just, I thought it's finished, so please.

**Felipe Abadia Bermeo** [20:31]:
> No, no, that I'm going to to.

> Correct the thing that you told me, Professor, about the outline, and I will will check

> the 17 node German topology and will continue if I have if I have questions, I'll let you know. Thank you.

**Qiaolun Zhang** [20:53]:
> You're welcome.

**Felipe Abadia Bermeo** [20:56]:
> Goodbye.

**Aryanaz Attarpour** [20:56]:

> Okay, thank you. If you need, if you have doubts about the German topology, you can send it to us as well, to me or to Jiaheng or...

**Qiaolun Zhang** [20:57]:
> Okay.

**Zheng Zhang** [20:58]:
> Thank you.

**Felipe Abadia Bermeo** [21:06]:
> There.

**Aryanaz Attarpour** [21:06]:

> to Prof Zhang as you wish, or to all of us.

**Felipe Abadia Bermeo** [21:08]:
> There.

> Yes, of course. Goodbye. Goodbye, everyone.

**Aryanaz Attarpour** [21:13]:

> Okay, goodbye. Thank you. Bye bye.

**Qiaolun Zhang** [21:16]:
> Okay, bye.

**Zheng Zhang** [21:16]:

> Goodbye, thank you.

> **Qiaolun Zhang** stopped transcription


