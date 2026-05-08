---
title: "Transcript: QoT-aware Light Paths Meeting"
date: 2026-04-23
tags: [transcription, QoT, light-paths, meeting]
status: completed
---

# Meeting Transcript: QoT-aware Light Paths (2026-04-23)

**Participants:**
- **Felipe Abadia Bermeo**
- **Aryanaz Attarpour**
- **Qiaolun Zhang**
- **Zheng Zhang**

**Context:** Meeting regarding the integration of Quality of Transmission (QoT) feasibility tools into the Multi-Agent System (MAS).

**Related Pages:**
- [[QoT_Awareness]]
- [[Tool_Registry]]
- [[Concepts_and_Terminology]]

---

## Transcript

**Aryanaz Attarpour** [0:47]:
> No, just. Okay, so this is a part of my work that I published in a conference. It is actually not a thing that you really need to think about it. It's just a part of a very small part of it.
> which is called QOT aware of the light paths. So what do we mean by QOT aware of the light paths? So what is the light path? So first thing first, I don't know how much is your optical knowledge. So I think Maybe you're not very familiar with the concepts of light paths. And because of that, I start to talking about the light paths. So whenever you think that I can skip, just let me know. Okay. Feel free to interrupt me, ask questions as you want.

**Felipe Abadia Bermeo** [1:26]:
> Yes, is. Okay. Yeah. Okay.

**Aryanaz Attarpour** [1:42]:
> So, let's assume that, so this is a this is a one example that I have a three node network, so I have 3 nodes of the network and I have 3 demands. These are the source, so let me, so these are the source nodes, these are the destination nodes, and these are the bit rates of the traffic that will go from, for example, node one to node two, node two to node three, and node two to node two. So these are traffics in the electrical layer. I want to send them to the fiber. In order to send them to the fiber, I need to, with a laser, I need to establish a light path.

**Aryanaz Attarpour** [2:27]:
> Okay, so what is light path? Light path is actually the light that is made by the laser that can carry my traffic. So we call it light path. So as an example here, so for example, this is node one, this is node two. So as you can see, this red... can be considered as a one light path that is generated from this board, which is we don't care about it because it is not your problem.

**Aryanaz Attarpour** [3:09]:
> Okay, so these are the light paths. So for the light paths, we want to check the QOT awareness. What is the QOT awareness? In the case that we consider means that, so when the light paths goes inside these fibers, it will be degraded. It will be at 10 weight.
> So there are many transmission impairments that impact this light path. So when we send this light path from these boards here, we send them with a power, with a specific power, which is called launch power.

**Aryanaz Attarpour** [3:52]:
> So we send them via a launch power, but when we receive the light path, it is not the same signal with the same power because the transmission impairments impacted these light paths during the transmission. So it... it is not that there is a noise, there is transmission impairments which affected that. So we need to make sure that when we send the light path, it will receive by the destination node.

**Aryanaz Attarpour** [4:29]:
> How we make sure with QOT, quality of transmission parameters. In our case, it is SNR, signal to noise ratio, and the other one is sensitivity of the receiver. that we check these two, that when the light path receives in the destination, it is above the power of the light path, must be above the defined threshold, which is -18 dBm. And we need to make sure that the SNR... The light path is above the defined threshold. So we can read it. So these are the two impairments that we are considering for the QOT awareness.

**Aryanaz Attarpour** [5:16]:
> We have a set of light paths. We need to make sure that these light paths are feasible, meaning that they receive to the destination with an SNR above the SNR threshold, and the power of the receiver is more than minus 18 dBm. So in order to check these two, we need to provide a set of amplifiers as an input to the problem, which in the code that I have, you can set the amplifiers. So it is very easy. Later, I mean, not today, but I will send you the code. And then again, I will have another call with you to show the code where is the part that you exactly need to take care about.

**Qiaolun Zhang** [6:23]:
> So like the slides here is a previous work of Aryanaz, so it's more complicated than what you need to do. So you don't need to like, yeah, get, yeah.

**Aryanaz Attarpour** [6:24]:
> Yeah, exactly. Don't worry. I mean, don't look at these OA placement and these traffic curving things. These are something very something that we really don't care about.

**Felipe Abadia Bermeo** [6:45]:
> Yes, for now, I care about... We are sending like the, well, the first node is the node one, for example, and we are measuring the SNR from there. No, we are generating a signal with SNR from there, and we are measuring the SNR in the next node, and we are measuring that. So, and we have to compare that the SNR in the second node is above a threshold that we, that the SNR thresh, not only the SNR but also DP underscore REC.

**Aryanaz Attarpour** [7:23]:
> Oh, okay. So the thing that you mentioned is that we are not calculating the SNR based on the nodes. So we don't calculate it node based. We need to calculate the SNRs in the network. So it is really important that, for example, from which fibers your light path passes. Okay, so because of that, it is not node based. So it is in a network, you need to calculate it. In the model that I provide to you, we calculate it through the network. So there is no need to change it. So you only, what you do, just you provide a setup like paths and a set of optical amplifiers. And then you just check if the feasibility is 1 or not one. If the feasibility is 1, it means that we have these two. OK?

**Aryanaz Attarpour** [8:43]:
> In order to calculate these network, in the network, we calculate the SNR of the light paths. We are using a specific model, physical layer model, which is called a Gaussian noise model or **GN model**.

**Aryanaz Attarpour** [9:02]:
> GN model. That there are some papers on this topic, but I think there is no need that you delve into it because it's unnecessary. It is an optical thing. And so we use that one. And also in order to make sure that the spans are working in their optimal power and these things, we also used another model called **logo model**. Locally optimized, globally optimized model.

**Felipe Abadia Bermeo** [9:45]:
> Yes, I would prefer to have an overview just to have context on the idea.

**Aryanaz Attarpour** [9:56]:
> Of course. So I will send you the two papers... and whatever question you have regarding them, you can ask me or Qiaolun or Zheng about it as you prefer.

**Aryanaz Attarpour** [10:34]:
> About the code, since my code is based on genetic algorithm, I have some genetic algorithm inside it and I don't want you to confuse you with that genetic algorithm stuff. I'm trying to remove that part. I try to remove as much as I can, but if I see it is taking too much time, I just remove a part and pass it to you. And then I'm always here if you have any questions, and I will show you which parts you need to take, because there are actually three functions that calculate this QOT awareness. So you just need that functions.

**Felipe Abadia Bermeo** [11:39]:
> Well, so this is, I should call it a function that I'm going to be using in my model, yes? So my system is going to, the operator is going to ask the system to use this function, yes? The system generates agents, the agents talk to each other, the agents use this tool and returns the value or the output of the tool to the operator.

**Aryanaz Attarpour** [12:17]:
> Yes.

**Qiaolun Zhang** [12:24]:
> Oh yes, it's correct, yeah.

**Felipe Abadia Bermeo** [13:05]:
> I have another question, but not about the program or the code. I followed instructions to connect to the VPN. I am connected to the VPN, but I don't know what is your workflow or what do you do usually when you're working. So do I have to connect to the VPN? Like when, how, why?

**Qiaolun Zhang** [13:25]:
> Also, it is mainly used to connect to the server in our lab, firstly to use some local AI model and also to access the test bed because you can only access a test bed via the internal network.

**Felipe Abadia Bermeo** [13:54]:
> The experiments that I have to do have to be in the testbed, or how I can experiment before the final version of a function?

**Qiaolun Zhang** [14:09]:
> I think I can firstly ask Mam to provide you another assistant professional group to provide you some codes that can already work with the test bed. And then, yeah, or if I now have some code, then we can also pass it to you.

**Qiaolun Zhang** [15:00]:
> Okay, and then I will ask them directly and then we can pass you the access to the test bed and also some existing codes we have before, because we published a paper in OFCOE talk... previously about how to use LLM to generate JSON file for the configuration of the test bed.

**Felipe Abadia Bermeo** [15:18]:
> Okay, thank you. Yes, I'll wait for that. And the final thing that I wanted to ask is, I see that you are working with Obsidian. Maybe you could give me some advice on the use of the program.

**Qiaolun Zhang** [15:40]:
> I think you can use Claudian, like Claudian code... it's the community plugin Claudian inside Obsidian... the main idea of use is that you can manage the text very well, and it can, because LLM can interact with markdown files very smoothly.

**Felipe Abadia Bermeo** [17:23]:
> One final question about what I said in the presentation 2 days ago, that I was planning to use langgraph as framework. Is that okay or do you have another maybe other framework that you prefer or?

**Qiaolun Zhang** [17:41]:
> Yeah, I think this is okay.

**Qiaolun Zhang** [18:07]:
> Yeah, we'll do it in next Tuesday and in next Monday before 8 A.m. You can upload your weekly report. I will send you the template and you can fill it... and then Zheng will talk with you. You need to arrange, ask Zheng about the issues you listed in the weekly report, and then Zheng will help you to solve this issue.

**Felipe Abadia Bermeo** [20:04]:
> Also, permission or access to download the recording and the transcription of the meeting.

**Qiaolun Zhang** [20:08]:
> I will send it to you later. I have no idea how to give the permission, but I can download it and send it via the chat.

**Qiaolun Zhang** [20:49]:
> No, see you. You're welcome.

**Aryanaz Attarpour** [20:51]:
> Thank you very much. Thank you. Bye bye.

**Qiaolun Zhang stopped transcription** [20:59]
