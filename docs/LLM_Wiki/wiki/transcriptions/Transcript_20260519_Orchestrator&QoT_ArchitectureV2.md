---
title: "Orchestrator & QoT Architecture V2"
date: 2026-05-19
tags: [transcription, meeting]
status: completed
---

# Meeting Transcript: Orchestrator & QoT Architecture V2 (2026-05-19)

**Participants:**
- **Aryanaz Attarpour**
- **Felipe Abadia Bermeo**
- **Jiaheng Xiong**
- **Qiaolun Zhang**
- **Zheng Zhang**

**Context:** Weekly thesis meeting.

---

## Transcript

**Qiaolun Zhang** [0:03]:

> Um...

> Me.

> We will give you access to other API later, but you can first use this one to set up the simulation.

> Um...

> To like to obtain the initial code, so...

**Felipe Abadia Bermeo** [0:19]:
> Okay.

**Qiaolun Zhang** [0:21]:

> OK, wait a second. Ohh. Yeah. Hey. Yes. But... Good. The. H.

> Yeah, maybe you can first start briefly talk about your progress, and then I will give you the API later.

**Felipe Abadia Bermeo** [2:25]:
> Yes, no problem.

**Qiaolun Zhang** [2:28]:

> Okay. So, maybe you can...

> Share the weekly report. I have already read it, but maybe others may not familiar with it. You can just quickly describe it and then we can discuss the next step or issues.

**Felipe Abadia Bermeo** [2:43]:
> Yeah. Yes.

**Qiaolun Zhang** [2:58]:
> ****.

**Felipe Abadia Bermeo** [2:58]:
> Only. Can you see the screen?

**Qiaolun Zhang** [3:11]:
> Yes, I can see your screen.

**Felipe Abadia Bermeo** [3:14]:
> A. So, this was the...

> The report for for this week.

> I talked with about it with Zhang yesterday, and basically I did.

> I work on into two things, the implementation and also the integration of the orchestrator. I analyzed the code base that you sent to me, Professor, last day. I don't remember when, but I analyzed it and I see what things can be.

> Fixed, not fixed, but improved from that script from that couple of days. I put them here.

> I also prepared a presentation. I don't know if you, if we should see, look at the presentation first, or I continue with the report.

**Qiaolun Zhang** [4:16]:

> Yeah, if you have prepared the presentation, we can see it together, but we can just quickly get the updates here and then see the presentation together.

**Felipe Abadia Bermeo** [4:25]:
> Yeah, yeah, OK, the plan goal.

**Qiaolun Zhang** [4:26]:
> Right.

**Aryanaz Attarpour** [4:27]:

> Here I can, can I say something? So I have a question. So do you plan to have the whole coat?

**Qiaolun Zhang** [4:36]:
> Sexuality.

**Aryanaz Attarpour** [4:38]:

> I mean, for the code that I sent you, do you plan to run the whole code?

**Qiaolun Zhang** [4:44]:
> Chen. Looks cool.

**Felipe Abadia Bermeo** [4:54]:
> That was a question for me.

**Aryanaz Attarpour** [4:54]:
> Can you hear me? Yes, that's a question from you.

**Qiaolun Zhang** [4:57]:
> Hello.

**Felipe Abadia Bermeo** [4:58]:

> Okay, no, I actually, that is something that I wanted to say in the presentation. I am not planning to use the whole code, only some functions.

**Qiaolun Zhang** [5:00]:
> Alright. Chen. Store. So, yeah, yeah.

**Aryanaz Attarpour** [5:10]:
> Okay, okay. Okay, perfect. Thank you.

**Qiaolun Zhang** [5:13]:
> So, it was for a minute, and then I'll do it.

**Felipe Abadia Bermeo** [5:17]:
> Okay, so the progress this week was that I...

**Qiaolun Zhang** [5:20]:
> Just. Chen.

**Felipe Abadia Bermeo** [5:24]:

> Well, I conducted an extensive analysis in the code base that I had sent to me, that is a C code base, and I identified that the wrapper, the wrapper approach that I then the last week maybe is not optimal in this scenario.

**Qiaolun Zhang** [5:34]:

> Sorry. Di. I.

**Felipe Abadia Bermeo** [5:44]:

> Because.

> And...

> The code base is a simulation and it's a complex simulation. So I analyze it and I saw some functions that we can implement directly in Python and put them into a tool, a tool, a land graph tool, so the orchestration, so the multi-agent system can use them.

**Qiaolun Zhang** [5:53]:
> T. Yes. Next time.

**Felipe Abadia Bermeo** [6:09]:
> I also, well, I drafted a proposal to do this. Maybe we can see the proposal and we can decide what to do. I, this is not the report that I...

**Qiaolun Zhang** [6:15]:
> ****. That was. **Felipe Abadia Bermeo** 6:23 This is, I'm sorry, this is not the report. report that I sent to you.

**Qiaolun Zhang** [6:28]:
> Shoot.

**Felipe Abadia Bermeo** [6:30]:
> It is this one.

**Qiaolun Zhang** [6:33]:
> See what we have to change a little bit.

**Felipe Abadia Bermeo** [6:33]:
> Yeah.

**Qiaolun Zhang** [6:35]:

> Yeah. Hello.

**Felipe Abadia Bermeo** [6:44]:

> I think I have to stop sharing one. For a bit this way.

**Qiaolun Zhang** [6:57]:
> That's right. That. Yeah, no problem. Guitar.

**Felipe Abadia Bermeo** [7:05]:

> Now, can you see my screen? Sorry.

**Qiaolun Zhang** [7:07]:

> Yeah. Yes, we can see your screen.

**Felipe Abadia Bermeo** [7:11]:

> Sorry, sorry, sorry. I, well, I drafted a proposal, then I reviewed the orchestrator that you sent.

**Qiaolun Zhang** [7:12]:

> Labib. Chen. So...

> What's up?

**Felipe Abadia Bermeo** [7:21]:

> And I also draw crafted a proposal to implement the orchestration or to take some ideas ideas of that code base and reform it, is restructured to to a new orchestration strategy.

**Qiaolun Zhang** [7:26]:

> Di. Just. Cortana. It will be happy. Yes.

**Felipe Abadia Bermeo** [7:39]:

> I am designing a second version of the architecture.

**Qiaolun Zhang** [7:41]:

> Smile. 20% longer.

**Felipe Abadia Bermeo** [7:46]:

> And I, with analyzing the orchestrator of code base, I see that the we can extract the topology of the test better.

**Qiaolun Zhang** [7:50]:

> That's all.

> I.

**Felipe Abadia Bermeo** [7:58]:
> via, via, it is a protocol called a restconf, so... And which is what I did, I did it this week.

**Qiaolun Zhang** [8:11]:

> Hosts.

**Felipe Abadia Bermeo** [8:12]:

> And then now I can present the implementation strategy that I that I worked on, yeah.

**Qiaolun Zhang** [8:19]:

> I have a quick question: So, did you try to look at the...

**Felipe Abadia Bermeo** [8:22]:

> Yeah.

**Qiaolun Zhang** [8:27]:

> Differences of your current work compared to existing works about agentic AI for.

**Felipe Abadia Bermeo** [8:31]:

> Yeah.

> Yes, I have. I have been doing that. I didn't prepare anything for today about that,

> but I have I have read some papers, I have some literature, and the work I did today is based also on that research I have.

**Qiaolun Zhang** [8:38]:

> Which? Nothing is like this.

> Chen.

**Felipe Abadia Bermeo** [8:53]:
> I have been doing.

**Qiaolun Zhang** [8:56]:

> Okay, perfect.

**Felipe Abadia Bermeo** [8:59]:
> OK, it's so.

**Qiaolun Zhang** [9:02]:

> Yeah.

**Felipe Abadia Bermeo** [9:04]:

> This is a presentation of about the like.

**Qiaolun Zhang** [9:05]:

> Okay. That's it.

**Felipe Abadia Bermeo** [9:08]:

> A new orchestrator architecture, and how can we implement the QT tool into these into our multi-agent system? I'm going to present the orchestration integration, the QOT integration, and finally how it would look like together, everything together.

**Qiaolun Zhang** [9:11]:

> Oops. Things. Singh. Exactly. So. ****.

**Felipe Abadia Bermeo** [9:28]:

> So, about the orchestrator, the one in the in the GitHub.

**Qiaolun Zhang** [9:29]:

> Bing. Yes, I did.

**Felipe Abadia Bermeo** [9:36]:

> Follows this logic: it first arrives to a planning phase, and then it arrives to an execution phase, and it is good. This actually is process of planning and execution is good and is the standard, and also another thing that is good about this orchestrator code base is that...

**Qiaolun Zhang** [9:43]:

> Sun.

> Two.

> Yeah.

> Okay. Play.

**Felipe Abadia Bermeo** [10:05]:

> Well, the communication with the API and the SDN controller is, well, very, very good for my work also, but the things that I think are important to note here is that this code base, this orchestrator is...

**Qiaolun Zhang** [10:11]:
> So. Slow.

**Felipe Abadia Bermeo** [10:24]:

> and it is not, it doesn't use cyclical reasoning because it's not done with LangChain and LangGraph. LangChain and LangGraph and LangGraph are the today's standard for multi-agent systems. This orchestrator is linear.

**Qiaolun Zhang** [10:28]:
> So, Peter.

> Sure.

**Felipe Abadia Bermeo** [10:44]:

> So it will not, it's not possible to interact with it in the same like conversation.

**Qiaolun Zhang** [10:48]:
> S.

**Felipe Abadia Bermeo** [10:53]:

> So, we can use this as base and transition to a line graph topology to a line graph. Topology, yes, so we can keep the pipeline logic, we can keep this step by step, like the intent, the planning, and the execution, and then the error handling, and we can keep the schemas and the way of communicating with the SDN controller.

**Qiaolun Zhang** [11:09]:

> The.

> Hosts.

> A

> I.

> Yeah.

**Felipe Abadia Bermeo** [11:25]:

> With the API and the test bed. Sorry, but we can replace the procedural script with some cyclical reasoning and the stateless memory with a hybrid memory. As I said in the last presentation, we can use like a hybrid approach of memory in this multi-agent system.

**Qiaolun Zhang** [11:31]:
> Play.

**Felipe Abadia Bermeo** [11:48]:

> with LM Wiki, with a state graph for the topology of the test bed, and with the rack for episodic memory and for documentation. And we can also introduce human in the loop in the validation for validation before the execution of

> of anything into the test bed. And also we can implement different nodes of human in the loop in different parts of the cycle as well.

> Now I can present some of the ideas that I had about the DQOT integration, and it is that now that we know that the topology that we can extract the topology, now that I know that I can extract the topology from the test bed.

> With the rest configuration, the rest protocol, we can. AM.

> Imagine, I imagine we can use a topology, we can implement a topology agent, a new agent that is in charge of...

> speaking like speaking with the SDN controller and get the retrieve the topology of the network and update with this topology update a graph and all this graph that is going to be stored in the RAM. It's going to be a X and can be accessed by. Every each agent in the multi-agent system.

> This would be the role of the topology agent, and then when we have all the like mapped the topology of the test bed into a graph, we can use.

> another agent like the routine agent to to to use use this tool of these QOT tool and extract the the or reason over the topology over over the graph the network the

> network graph that we

> A hat that we retrieved from the code base from the test bed, sorry, so we can extract the most important functions of the network CPP that is the file in the code base that Aryanaz sent it to me, we can translate it. Translate them into Python.

> Following the like the.

> Language of LandGraph, like the framework of LandGraph, the functions that I think are important are the calculated demand SNR, the calculated propagated SNR, and the span SNR, and we can query the topology directly from the knowledge graph. So the tool can use this topology, like can use the nodes and the path that are stored in the knowledge graph. And it outputs the, it performs the calculation and outputs the SNR, the power, and the feasibility to the routing agent.

> And then the routine agent reason over these and passes the information to the orchestrator or to the whole system to act over the test bed or to return information to the operator.

> In the right, I put a flow graph. For example, we can see here that if the calculation returns that it is feasible to use this path, we can implement also a light path agent to control the test bed to access to the...

> ONDM controller.

> And this is how it would look like the whole architecture of the orchestrator with the routing agent, like the routing agent that is going to be using the QOT tool. We first begin with the user.

> Intent, like the operator intent, here we rip.

**Qiaolun Zhang** [16:08]:

> Well, I think Aryanaz has a question. Maybe, Aryanaz, you can ask.

**Felipe Abadia Bermeo** [16:12]:

> Oh, sorry.

**Aryanaz Attarpour** [16:15]:

> Thank you. Yes, I have a question from the previous slide.

**Qiaolun Zhang** [16:15]:

> Mostafa.

> Mostafa. But. Hello!

**Aryanaz Attarpour** [16:22]:
> If you can show, yes, so here. **Felipe Abadia Bermeo** 16:22 Yeah.

**Aryanaz Attarpour** [16:26]:
> I...

> Don't get that checks graph. So what is the output of that check graph?

**Qiaolun Zhang** [16:33]:
> Okay, no. **Felipe Abadia Bermeo** 16:35 And the chick.

**Aryanaz Attarpour** [16:36]:

> I mean, that checks graph go to the knowledge graph, right?

**Felipe Abadia Bermeo** [16:41]:

> Yes, yes, yes. With this, I mean the knowledge graph is updated or is maintained by the topology agent that I showed here.

**Aryanaz Attarpour** [16:42]:
> Okay.

**Qiaolun Zhang** [16:46]:

> ****. Sam, thank you. She does.

**Aryanaz Attarpour** [16:52]:
> Okay.

**Felipe Abadia Bermeo** [16:54]:

> The knowledge graph contains the topology of the SDN of the test bed, the current topology of the test bed.

**Qiaolun Zhang** [16:57]:
> Chen.

**Aryanaz Attarpour** [17:00]:
> Piero.

**Felipe Abadia Bermeo** [17:03]:

> A DQD tool can access to, yes, please.

**Aryanaz Attarpour** [17:03]:

> Yeah, I just have a question. I don't know this, to be honest, so I'm just asking. So, shouldn't the knowledge graph, I mean, the knowledge graph must be updated regardless of the feasibility of the road.

**Qiaolun Zhang** [17:15]:

> It's for the paper now. Of course.

**Felipe Abadia Bermeo** [17:22]:
> Yeah.

**Aryanaz Attarpour** [17:23]:

> Okay.

**Qiaolun Zhang** [17:23]:

> You know, I see.

**Aryanaz Attarpour** [17:25]:
> Okay.

**Felipe Abadia Bermeo** [17:26]:
> Yeah.

**Aryanaz Attarpour** [17:27]:

> Perfect. Okay, now I understand. Thank you.

**Qiaolun Zhang** [17:30]:
> P.

**Felipe Abadia Bermeo** [17:31]:

> Okay. Eh.

> So I was explaining this, the flow chart. We begin with the intent of the operator. Here we replace the planning phase of the orchestrator script that you sent me. Here we replace it with a supervisor node, a Liangyu supervisor node.

**Qiaolun Zhang** [17:35]:

> The. HR. Right, okay. Hey, Cortana. Six.

**Felipe Abadia Bermeo** [17:54]:

> And we implement, we put here a node of human in the loop to iterate over the iterate over the intention of the operator, and just when the operator says that, or when the operator allows the system to.

**Qiaolun Zhang** [17:57]:

> So.

> Yes.

**Felipe Abadia Bermeo** [18:16]:

> Execute, then we implement this land graph land graph node to divide the tasks to send it to the agents what they should do, and we here it depends on the intent, but, but for example, we can go first to.

**Qiaolun Zhang** [18:35]:

> So.

**Felipe Abadia Bermeo** [18:37]:

> To the topology agent, the topology agent will retrieve.

**Qiaolun Zhang** [18:38]:

> Sing, Sing.

**Felipe Abadia Bermeo** [18:43]:

> The.

> We retrieve the topology from the test bed, and we'll update the graph with that topology. Then, with that graph updated, the routing agent can access to this graph and reason over that.

**Qiaolun Zhang** [18:54]:

> The Hunt. Ehsan.

**Felipe Abadia Bermeo** [19:02]:

> And and uses using the QOT tool and uses the QOT tool to.

**Qiaolun Zhang** [19:04]:
> Stop.

**Felipe Abadia Bermeo** [19:09]:

> To validate if a route or a path is feasible, depending on the also depending on the intent of the user, and the returns, the feasibility or not feasibility, and the value of the SNR to the orchestrator, and well, here we can, depending on the...

**Qiaolun Zhang** [19:15]:

> Okay. Sorry. Yes.

**Felipe Abadia Bermeo** [19:29]:
> On the intent, we can iterate through this. This is cyclical, and it's the main difference between this multi-agent system with the orchestrator of the repo. This is cyclical, so it has an end only when all tasks are done.

**Qiaolun Zhang** [19:30]:

> Just. Yeah. Start. So.

**Felipe Abadia Bermeo** [19:48]:

> And the user has no more questions or nothing more to do with with the system.

**Qiaolun Zhang** [19:53]:

> Okay. Yes.

**Felipe Abadia Bermeo** [19:56]:

> That is it. Well, the like path agent I put it here like is an idea. This would be with would be replacing the execution process, the execution path, because this like path agent would be in charge of.

**Qiaolun Zhang** [20:02]:
> Listen.

**Felipe Abadia Bermeo** [20:14]:

> Controlling, or yes, controlling the SDN to change the test bed. And that's it for the presentation.

**Qiaolun Zhang** [20:25]:

> ****.

**Felipe Abadia Bermeo** [20:28]:
> So, thank you. Yeah.

> Hey, I don't know if we can discuss so discuss on this, so...

**Qiaolun Zhang** [20:33]:

> Can you go back to? Shut up.

**Felipe Abadia Bermeo** [20:38]:
> Yep.

**Qiaolun Zhang** [20:40]:

> Can I go back to the presentation? I just want to double-check.

**Felipe Abadia Bermeo** [20:42]:
> Yes.

> The chart, the flow chart is not the same that I sent it yesterday because I today I did some changes, but I can send it, send the new document, update it.

**Qiaolun Zhang** [20:47]:
> That said, the latest that are not fixed. Okay. So, your first SEO and test bed API, there might be an REST error. So. You have, you first have the... Wait a second, so in step 5. You wrote the task.

**Felipe Abadia Bermeo** [21:27]:

> Yoann.

**Qiaolun Zhang** [21:28]:

> And then?

> Um...

> After the task, you also send final JSON payload to the test bed to see if it works or not. If it doesn't work, we return the rest error. Is it correct?

**Felipe Abadia Bermeo** [21:48]:

> Yes, that's correct. Actually, this everything after the...

**Qiaolun Zhang** [21:49]:

> Play. Are you? Chen. It was cheap.

**Felipe Abadia Bermeo** [21:56]:

> The 5th step and everything related to the light path agent is speculative. It can be improved because till now, till now I have the routing agent idea and the topology agent idea. This is more like to act.

**Qiaolun Zhang** [21:58]:

> See it when. Oops. Yeah. Hello! Open contest.

**Felipe Abadia Bermeo** [22:14]:

> over the test bed, but we are not yet, I am not yet thinking or acting over the test bed, just retrieving information from it.

**Qiaolun Zhang** [22:20]:

> Cesare.

> Okay, okay, got it. Yeah, one suggestion is that if you have numbers in some lines, it's better to put numbers before the lines.

**Felipe Abadia Bermeo** [22:40]:
> Okay.

> Yes, yes, yes.

**Qiaolun Zhang** [22:43]:

> Okay, yeah.

> And.

> And then I need to, I think I need to remind Mam to give you access to the test bed. I think.

> Okay, I think she forgot to do it, but... Um...

> No.

**Aryanaz Attarpour** [23:09]:

> Here, just a question, another question, so after that blue box.

**Qiaolun Zhang** [23:10]:
> In Boutaba.

**Felipe Abadia Bermeo** [23:15]:
> Yeah.

**Aryanaz Attarpour** [23:15]:

> So we wrote the task simultaneously to topology agent and routing agent.

**Qiaolun Zhang** [23:17]:

> Next. Just.

**Felipe Abadia Bermeo** [23:24]:

> Not necessary. It may not be simultaneous. It depends on the intent. The orchestrator

> or the this node in Liangyu is like smart enough to determine if the root, if it routes the task, the task first to an agent and then to another agent.

**Qiaolun Zhang** [23:30]:
> The.

**Aryanaz Attarpour** [23:31]:
> Okay.

**Felipe Abadia Bermeo** [23:43]:
> Or...

> can be simultaneously. And it depends because maybe in some cases, one agent would need the output of another agent. So it cannot perform any task in that moment. So it depends. It depends. It can be simultaneously, or it can be one and then another.

**Aryanaz Attarpour** [23:54]:
> Mëmëdhe.

**Qiaolun Zhang** [23:55]:
> Chen. Six. **Aryanaz Attarpour** 23:58 Okay. **Qiaolun Zhang** 23:59 Yeah.

**Aryanaz Attarpour** [24:00]:
> Okay. Okay, thank you.

**Zheng Zhang** [24:13]:

> Hi, Felipe. Maybe I lost. I want to ask you the...

**Qiaolun Zhang** [24:14]:
> Atazad.

**Felipe Abadia Bermeo** [24:15]:
> Hello.

**Qiaolun Zhang** [24:18]:
> Okay.

**Zheng Zhang** [24:21]:

> Three, 4, 5, yeah, all routine tasks, right?

**Qiaolun Zhang** [24:22]:

> Bing. So.

**Zheng Zhang** [24:30]:

> What is the difference between among them, and you can do the routing task by different ways?

**Felipe Abadia Bermeo** [24:42]:

> Sorry, Chen, can you repeat the question? What is the difference between...

**Zheng Zhang** [24:46]:

> Yeah, what I want to ask if the difference between the three, 4, 5.

**Qiaolun Zhang** [24:52]:

> Fox.

**Felipe Abadia Bermeo** [24:53]:

> Between this root task, this root task, and this root task, right? They are they are different tasks. They are not the same tasks, but the task depends on the intent of the user. It can be two tasks, it can be 10 tasks, and each agent is responsible of...

**Zheng Zhang** [24:58]:
> Uh, yes, yes, I... Oh.

**Qiaolun Zhang** [25:09]:
> So...

**Felipe Abadia Bermeo** [25:13]:
> Doing a set of tasks depending on the profession of that agent. For example, the topology agent would be in charge would be in charge of the tasks related to extracting the topology from the test bed. Yeah.

**Qiaolun Zhang** [25:19]:

> So. S.

**Zheng Zhang** [25:22]:
> Mm.

**Felipe Abadia Bermeo** [25:33]:

> And updating the knowledge graph, but the routing agent would be in charge of tasks related to the calculation of the of the SNR, or to see if a path is feasible or if not feasible, and all these routing tasks.

**Zheng Zhang** [25:36]:

> Okay.

**Felipe Abadia Bermeo** [25:52]:

> Are done by the by this language of node, like the orchestrator, that it is smart enough to know which agent is which agent does which thing.

**Qiaolun Zhang** [26:00]:

> The.

> Chen.

**Felipe Abadia Bermeo** [26:05]:

> Or which task?

**Qiaolun Zhang** [26:06]:

> No.

**Zheng Zhang** [26:08]:

> Okay, thank you. Now I understand. And I think you can show some examples of different intent requests.

**Qiaolun Zhang** [26:08]:

> Okay. Yeah. Stop. In the da. She said if you.

**Felipe Abadia Bermeo** [26:19]:

> Oh, okay.

**Zheng Zhang** [26:19]:

> And based on different intent promotes and requests, you can conduct different pipelines.

**Qiaolun Zhang** [26:23]:

> Yeah.

> Is upward.

> Chen.

**Felipe Abadia Bermeo** [26:29]:

> A.

> Yes, I would have to to see. I also want to think on on intense. I I am not sure about.

**Qiaolun Zhang** [26:35]:

> The. Lost in heaven.

**Zheng Zhang** [26:38]:
> Yeah.

**Qiaolun Zhang** [26:39]:
> Yes.

**Felipe Abadia Bermeo** [26:44]:

> exactly how an intent of a complete intent end to end would look like, but I imagine that an intent, a simple intent can be like the operator is the operator wants to know if establishing a light path between 2 nodes following a path is feasible or not feasible and asks the system.

**Qiaolun Zhang** [26:54]:
> I.

**Felipe Abadia Bermeo** [27:04]:

> Can I establish a server, a service between these two nodes and the system calls the routing agent, uses the QoT tool, and then replies to the user responding, saying if it is not feasible or it is not feasible and...

**Qiaolun Zhang** [27:06]:
> Sezin. You. Stop. It. Big. Yeah.

**Felipe Abadia Bermeo** [27:27]:
> What suggestions does it have?

**Zheng Zhang** [27:30]:

> Okay, thank you. And I also want to ask about the different tasks that are generated from the intent. If the task, do you have any idea about the routine task? What is it about?

**Qiaolun Zhang** [27:34]:
> Start.

> H.

**Zheng Zhang** [27:53]:

> Establish, let pass, or doing some computing tasks.

> Because previously, when we talk about it, we also consider about the computing layer, the computing resources.

> Do you have any idea about the task?

**Felipe Abadia Bermeo** [28:16]:

> I'm really sorry, Zheng. I don't know if... Can you repeat the question? I'm having troubles with the...

**Qiaolun Zhang** [28:22]:
> The.

**Zheng Zhang** [28:25]:

> Okay, okay, because previously, at the beginning, we talk about the objective. We also consider computing resources. Do you consider it in routing task?

**Felipe Abadia Bermeo** [28:47]:
> Mm.

**Qiaolun Zhang** [28:47]:

> SALA. Yeah.

**Felipe Abadia Bermeo** [28:49]:
> And I don't know, no.

**Zheng Zhang** [28:54]:
> So, what is the routine task now you are you considering?

**Qiaolun Zhang** [28:57]:
> Have you? Just.

**Felipe Abadia Bermeo** [29:03]:
> Sorry. **Qiaolun Zhang** 29:05 I think we are just considering our basic setup for now. We're just...

**Felipe Abadia Bermeo** [29:05]:
> Eh.

**Zheng Zhang** [29:09]:
> Mm.

**Felipe Abadia Bermeo** [29:10]:
> Yeah.

**Qiaolun Zhang** [29:11]:
> So, considering, like, a light pass.

**Zheng Zhang** [29:15]:
> Okay.

**Qiaolun Zhang** [29:16]:

> I think that would be something we might consider after we finish your initial setup.

**Zheng Zhang** [29:23]:

> Yeah. Okay.

**Qiaolun Zhang** [29:30]:
> Thank you.

**Felipe Abadia Bermeo** [29:31]:
> Yeah, because for now, for now, I think we need like a basic setup, yes.

**Qiaolun Zhang** [29:33]:
> We want to... I should get it.

**Zheng Zhang** [29:37]:
> Okay.

**Felipe Abadia Bermeo** [29:43]:
> And...

> I don't know if you, well, I think I have to send to Chen the code base that Aryanaz sent me. I don't know if I can because of the paper I signed, but...

**Qiaolun Zhang** [29:50]:

> I.

> S.

**Aryanaz Attarpour** [29:59]:

> No, no, you cannot do that.

**Felipe Abadia Bermeo** [30:02]:

> Okay, yes, because Chen wants to be sure if those functions that I said.

**Qiaolun Zhang** [30:02]:

> Just kidding.

> I.

**Felipe Abadia Bermeo** [30:10]:

> Here, in this light, Di.

**Qiaolun Zhang** [30:10]:

> Yeah, but what if like Zhang also signed this paper? Maybe you can share it with Zhang, is it correct?

**Aryanaz Attarpour** [30:19]:

> You need to talk about it with Prof that this NBA thing is under his supervision. So if when I return, I will talk with Prof to see if we can, if it is possible.

**Qiaolun Zhang** [30:19]:

> Schieppati.

> Hosts.

**Aryanaz Attarpour** [30:36]:

> possible that Zheng also signs the NDA, but also I can help you if you need help, but of course I do check if Zheng needs help.

**Felipe Abadia Bermeo** [30:36]:

> Okay. Okay.

**Aryanaz Attarpour** [30:44]:

> To sign an NDA, and I will let you know, Chen.

**Qiaolun Zhang** [30:47]:

> telephone.

**Felipe Abadia Bermeo** [30:48]:

> Okay, for now, for now, I think that these functions are the ones that I have to like translate into Python.

**Qiaolun Zhang** [30:53]:

> Stop.

> G.

**Felipe Abadia Bermeo** [31:01]:

> Because, well, I analyzing the the code base, I sir.

**Qiaolun Zhang** [31:06]:

> Go.

> Yeah, yeah, don't worry. There was just one student passing by, yeah.

**Felipe Abadia Bermeo** [31:11]:

> Yeah.

> Yeah, hey, analyzing the code base. Well, I see that the calculated Madison R is the one. Well, here, here are like...

**Qiaolun Zhang** [31:18]:
> Six.

**Felipe Abadia Bermeo** [31:25]:

> Also, these two functions, and it it calculates the SNR, it calculates the power, and it determines if it is feasible or not feasible, and well, I would have to analyze it deeper to understand very well how does how the function works and how can I translate it to Python.

**Qiaolun Zhang** [31:36]:

> Zhao.

> Ch. Okay.

**Felipe Abadia Bermeo** [31:54]:

> And that's it.

**Qiaolun Zhang** [31:55]:

> Do you have any questions here?

**Felipe Abadia Bermeo** [31:58]:

> Yes, I have only one, well, two questions. We have there in the simulator, these

> constants in the C code, these constants that Aryanaz told me that, well, we can change them in the simulator, but I don't know that.

**Qiaolun Zhang** [32:00]:
> Di.

> Yes, you do.

**Felipe Abadia Bermeo** [32:16]:

> Now that we are planning to extract the topology from the test bed, this should remain constants and we should map them into a schema, or if we are querying them dynamically as well. That would be the first question. And I also would like to...

**Qiaolun Zhang** [32:27]:
> Sun.

**Felipe Abadia Bermeo** [32:37]:
> To have.

> Well, this like the measurement of of the SNR in the test bed of between between to between to node or in a path to.

> to see if my, well, no, not my, to see if the code, the quality of transmission.py works well. That would be in the future, not now, because I already have to start implementing it.

**Qiaolun Zhang** [32:58]:

> Sister. This.

**Aryanaz Attarpour** [33:07]:
> Okay, so about the first question, you can consider it done fixed.

**Felipe Abadia Bermeo** [33:13]:
> OK.

**Aryanaz Attarpour** [33:13]:

> So they are like static as they are. About the second question that you mentioned, to

> be honest, there is a... implementation problem with that test bed.

**Qiaolun Zhang** [33:26]:
> Say it.

**Aryanaz Attarpour** [33:30]:

> because the test bed is connected with a very short fibers.

**Qiaolun Zhang** [33:33]:
> Hosts.

**Felipe Abadia Bermeo** [33:36]:
> Okay. Yeah.

**Aryanaz Attarpour** [33:38]:

> And there is no inline amplifiers as well.

> along the fibers. So we have only preamp and booster in each radar. So one thing is that if the fiber is not long enough, and since we also have optical amplifiers inside the node, the SNR would be very high.

**Felipe Abadia Bermeo** [33:42]:

> Yeah.

**Aryanaz Attarpour** [34:03]:

> So we cannot see the degradation and very, how we say, the SNR, which is very low. The SNR would be definitely above the threshold.

**Felipe Abadia Bermeo** [34:04]:
> Yeah, I understand that. Yeah, yeah.

**Aryanaz Attarpour** [34:17]:

> So this is the first problem about the implementation that we have. We are trying to solve that issue by borrowing some file from other group.

**Felipe Abadia Bermeo** [34:31]:
> Okay.

**Aryanaz Attarpour** [34:33]:

> So yeah, I need to check when I came back. I will ask from Alberto that if they have a longer fiber and we can borrow it. So in that case, I think it would be okay.

**Felipe Abadia Bermeo** [34:48]:

> Okay, I understand.

**Qiaolun Zhang** [34:49]:

> S.

**Aryanaz Attarpour** [34:49]:

> But for now, consider question one as static and consider that the SNR would be super high.

> So you should not have a specific problem. So to be honest, all the roads that you are going to consider probably will be feasible.

**Felipe Abadia Bermeo** [34:57]:

> Yes, okay.

**Qiaolun Zhang** [35:01]:

> Just.

> Yeah.

**Felipe Abadia Bermeo** [35:08]:

> Yes, I understand, I understand. But it will, the, okay, I understand, but I think here the important thing is to see if the orchestration, if the orchestrator, like the multiagent system, can interact with the test bed and they will do this reason, this cyclic reason.

**Aryanaz Attarpour** [35:09]:

> If you want to test it on the test, but...

**Qiaolun Zhang** [35:15]:
> Bing.

**Felipe Abadia Bermeo** [35:29]:
> So, even if Di.

> the path is not feasible, well, the agent should be able to understand that it's not feasible and to reply to the operator. It also works.

**Qiaolun Zhang** [35:33]:
> It.

**Aryanaz Attarpour** [35:42]:

> Yeah.

**Qiaolun Zhang** [35:43]:
> Just.

**Felipe Abadia Bermeo** [35:46]:
> So, it doesn't matter.

**Aryanaz Attarpour** [35:46]:

> Okay, yes, yes, this is the main goal. Exactly. So as I mentioned, so for now it is consider it as I mentioned. And then I will come back and try to find some fiber so we can put the longer fibers and see also that case. So you can also test it on the test.

**Felipe Abadia Bermeo** [36:04]:

> Tareef. There. Yeah. That would be it. And, well, for continuing.

> Here with Di.

> report, the things I have planned for next week are, well, today the presentation and started the QOT, the QOT translation tool to Python.

> The of the functions that I said, and then I can start the stage graph implementation also.

**Qiaolun Zhang** [36:55]:

> I have a question here. So do you think it's necessarily necessary to translate the QOT to Python? Maybe you can just use Python to call the C code and obtain the result.

**Felipe Abadia Bermeo** [36:58]:

> Yeah.

> It.

> Yeah, I think it can be done like that, but I would prefer it to be a function like nothing for LandGraph, a Python for LandGraph because it is LandGraph uses well, this type of files, this.py files.

**Qiaolun Zhang** [37:21]:
> The.

**Felipe Abadia Bermeo** [37:28]:

> And I don't know how it would work with.

> A different approach, but I can I can explore the explore the option.

**Qiaolun Zhang** [37:38]:

> St.

> Yeah, maybe like.

> You could have a Python function that calls the C code and read the results.

**Felipe Abadia Bermeo** [37:56]:

> I, I, I will say yes, it could, it can be done. I think it can be done, yes.

**Qiaolun Zhang** [37:57]:

> And...

> Yeah, maybe it is faster, yeah.

**Felipe Abadia Bermeo** [38:03]:

> I will consider the two options.

**Qiaolun Zhang** [38:06]:
> Okay.

**Felipe Abadia Bermeo** [38:06]:
> If I will consider the two options.

**Aryanaz Attarpour** [38:10]:
> Now, I remember that Zheng might have the code, the C code. Zheng, do you remember that the multi-band code in C is QOT or not?

**Qiaolun Zhang** [38:20]:

> And. Yes.

**Zheng Zhang** [38:24]:

> Ohh, yes, I remember that are the are this codebase seen?

**Qiaolun Zhang** [38:27]:

> Yes. Yes.

**Aryanaz Attarpour** [38:32]:

> Yeah, I think it's the same code Zheng.

**Qiaolun Zhang** [38:35]:

> Did it come to a test?

**Zheng Zhang** [38:35]:
> Okay.

**Aryanaz Attarpour** [38:37]:

> You, if you check in that code, you should find that three functions that Felipe mentioned: calculate a span SNR, calculate the SNR, and calculate propagation. What was it, Felipe?

**Qiaolun Zhang** [38:39]:
> Sign that. Bing.

**Zheng Zhang** [38:45]:
> Okay.

**Qiaolun Zhang** [38:47]:
> Just, well. Stop.

**Zheng Zhang** [38:53]:
> Okay, perfect. **Aryanaz Attarpour** 38:55

> Yeah, in that, I took it exactly from the same code. Then I will come and give you the code.

**Qiaolun Zhang** [38:59]:
> It.

**Zheng Zhang** [39:03]:
> Oh, no worries. If we are seeing, I can use the previous one.

**Aryanaz Attarpour** [39:04]:
> Okay. Okay. **Zheng Zhang** 39:09 Okay, thank you.

**Aryanaz Attarpour** [39:11]:

> Thank you.

**Qiaolun Zhang** [39:25]:

> Okay, yeah, I will send the API to you later. Do you have any other questions?

**Felipe Abadia Bermeo** [39:31]:

> For now, I don't. Thank you for the attention.

**Zheng Zhang** [39:32]:

> Di.

**Qiaolun Zhang** [39:33]:

> Yeah, I think for...

> Yeah, I think for the next action points, um...

> You can also list a table or make one, two slides to summarize the differences of the current setup compared to the literature.

**Felipe Abadia Bermeo** [39:54]:
> OK.

**Qiaolun Zhang** [39:55]:

> Okay, yeah, I think that's all. If you don't have other questions, we can answer the meeting. I think the progress is nice, yeah.

**Felipe Abadia Bermeo** [39:58]:

> Mm.

> Yes, sir.

> Okay, thank you, Professor. Thank you, Chen. Thank you, Aryanaz, and thank you, Jiaheng.

**Qiaolun Zhang** [40:09]:

> You're welcome.

> Station.

> Yes, thank you, too.

**Aryanaz Attarpour** [40:16]:
> You're welcome. Thank you.

**Zheng Zhang** [40:17]:
> Thank you.

**Felipe Abadia Bermeo** [40:17]:
> Goodbye.

**Qiaolun Zhang** [40:19]:
> Bye.

**Zheng Zhang** [40:19]:
> Bye.

**Aryanaz Attarpour** [40:19]:
> Bye-bye.

**Qiaolun Zhang** [40:21]:

> Bye, have a good day.

**Felipe Abadia Bermeo** [40:21]:

> Can you send the transcript of the record after the end of the meeting? Thank you, Professor.

**Jiaheng Xiong** [40:22]:
> Um...

**Qiaolun Zhang** [40:24]:
> Yeah.

> Sure, sure. Okay, bye.

**Felipe Abadia Bermeo** [40:30]:
> Goodnight.

**Zheng Zhang** [40:31]:
> Bye.

> **Felipe Abadia Bermeo** stopped transcription


