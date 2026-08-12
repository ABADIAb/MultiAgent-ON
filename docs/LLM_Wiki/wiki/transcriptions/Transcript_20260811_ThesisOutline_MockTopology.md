---
title: "Thesis Outline Feedback & Mock Topology Strategy (Cleaned)"
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

**Context:** Cleaned and consolidated Teams meeting transcript.

---

## Transcript

**Qiaolun Zhang** [0:03]:
> We introduce why we perform this study and provide background, typically called motivation. You don't need separate subsections for motivation (like 1.1 and 1.2)—that makes it feel too much like background and related works. Focus directly on the proposed solution and contribution.

**Qiaolun Zhang** [1:09]:
> For this part, you can call section 1.3 "Overview and Motivation", putting the previous background material inside. Before the research gap, the preceding 2 or 3 subsections should be parallel. Regarding the subsection titles, it's better not to use "Limitation" in the title itself, though you can comment in the text on why previous works aren't sufficient.

**Qiaolun Zhang** [3:00]:
> We don't need overly detailed subsection titles like "Reliance on Post-deployment retry loops"—that's too concentrated on one specific topic. Instead, provide a higher-level summary in section 2.1 of what has been done in agent design for LLMs, without focusing too narrowly on a single component like retry loops.

**Qiaolun Zhang** [4:48]:
> Regarding Section 5 (System Model / Implementation / Setup), we typically do not have a dedicated subsection (like 5.5) for comparison with baselines. Instead, baseline comparisons should be integrated directly into each evaluation subsection (e.g., 5.3 and 5.4) when evaluating metrics across all solutions together.

**Qiaolun Zhang** [6:27]:
> Revise the outline and send me another version. I will check it and write an email to Professor Chen so he is aware of your October graduation timeline and we can organize the defense committee members.

**Aryanaz Attarpour** [7:17]:
> Sorry for joining late. Regarding your email, Felipe, you mentioned missing topology information, specifically the exact physical fiber span lengths between testbed nodes. The physical testbed we have uses very short fiber span lengths (under 1 kilometer). For good numerical evaluation results, I suggest using larger network topologies (such as German or Japan topologies) and using their standard fiber lengths.

**Qiaolun Zhang** [8:29]:
> Felipe, we should consider a topology with a larger number of nodes for the main evaluations. If Mëmëdhe can share testbed data, we could still use that for small preliminary tests.

**Aryanaz Attarpour** [8:34]:
> Exactly, testbed fibers aren't even 1 km long, so for numerical results, it's better to use larger topologies like the German or Japan networks. Also, regarding the expected operational gains of EDFAs, you can check the amplifier gain settings in the C++ simulator files `OA_loc.cpp` and `OA_loc.h`.

**Felipe Abadia Bermeo** [10:10]:
> Originally, the plan was to build the topology directly from the physical testbed via a GET API endpoint to retrieve physical attributes, but that endpoint isn't available. So now we're planning to mock the testbed topology. In the future/contributions section, we can mention that automated topology retrieval from a live testbed can be implemented as future work.

**Aryanaz Attarpour** [11:36]:
> Mocking the topology makes a much stronger case. The physical testbed lacks inline amplifiers (ILAs), so mocking standard topologies allows you to test realistic setups with ILAs and state that the approach can be adapted to physical testbeds in the future.

**Felipe Abadia Bermeo** [12:07]:
> Right, the physical testbed has only 3 nodes, so mocking a larger testbed yields much better simulations. In the simulator, I mocked a 3-node topology, but I can expand it to more nodes and amplifiers. Could you suggest a specific topology and node count?

**Aryanaz Attarpour** [12:54]:
> We can use the 17-node German topology or a 14-node Japan topology.

**Aryanaz Attarpour** [13:23]:
> I think the 17-node German topology is best because it has longer fiber spans, allowing us to place more optical amplifiers compared to the Japan topology. You can find the topology details, fiber lengths, and connectivity online.

**Felipe Abadia Bermeo** [14:18]:
> Perfect, I found the 17-node German topology specifications online. Next, could you help me define a set of operational intents to evaluate the system? For example, requesting a lightpath between two nodes with specific constraints, so we can test different intent characteristics.

**Aryanaz Attarpour** [15:19]:
> Definitely, I will draft and share example operational intents with you.

**Felipe Abadia Bermeo** [15:40]:
> I also wanted to ask about the Kimi API: is there a way to reduce the thinking/reasoning process or latency of the LLM? It's spending time on unnecessary thinking. Also, I'd like to check token usage and model versions (V1 vs V2/V3) to evaluate token consumption in our experiments.

**Qiaolun Zhang** [16:39]:
> You can try updating the API version to V2 or V3. Regarding token usage, the platform interface for the Kimi coding plan makes token count tracking a bit hard to see. We might also consider evaluating one or two other LLM models. I will check and provide more details.

**Felipe Abadia Bermeo** [19:17]:
> Thanks, Professor. Also, I'm moving back to Milan on September 1st to look for a job there, as I already have an apartment setup. So having our meeting on that Tuesday might be difficult.

**Qiaolun Zhang** [19:29]:
> Understood, we can hold our next meeting in September instead.

**Felipe Abadia Bermeo** [20:31]:
> Perfect. I will revise the thesis outline per your feedback, configure the 17-node German topology in the simulator, and follow up if any questions arise. Thanks everyone!
