export type StoryTranslation = {
  text: string
  replies?: { label: string; say: string }[]
}

export const englishStory: Record<string, StoryTranslation> = {
  '1-0': {
    text: 'A spacecraft watches Earth. Down below, a farming community in Mozambique needs help with rain, heat, and soil.',
  },
  '1-1': {
    text: 'I received a signal from Earth: the farm is struggling. I will land near the community.',
  },
  '1-2': {
    text: 'A machine fell from the sky! Who could it be?',
    replies: [
      { label: 'Hello!', say: 'Hello! Who are you?' },
      { label: 'That machine?', say: 'Where did that machine come from?' },
      { label: 'I can see', say: 'I have never seen anything like this.' },
    ],
  },
  '1-3': {
    text: 'I come from space. I am on a mission to help farming communities understand the environment and protect their crops.',
  },
  '1-4': {
    text: 'We have many problems here.',
    replies: [
      { label: 'The rain', say: 'Sometimes we do not know when it will rain.' },
      { label: 'The plants', say: 'Our crops do not grow as we expected.' },
      { label: 'The heat', say: 'The heat is harming the land too.' },
    ],
  },
  '1-5': {
    text: 'That is exactly why I am here. I brought the AgroSpace Mission Manual.',
  },
  '1-6': {
    text: 'This manual is your guide. Each mission teaches you about climate, water, soil, and crops. You will investigate and make decisions.',
  },
  '1-7': {
    text: 'So this manual solves every problem?',
    replies: [
      { label: 'Show me the manual', say: 'Show me the manual.' },
      { label: 'Does it solve everything?', say: 'Will this manual tell me how to solve all our problems?' },
      { label: 'Let us work together', say: 'I want to learn with the community.' },
    ],
  },
  '1-8': {
    text: 'It will help you find answers. But you will need to investigate. Not every solution works on every farm.',
  },
  '1-9': {
    text: 'Mission 01 complete. The farmer, the astronaut, and the community begin their AgroSpace adventure.',
  },
  '2-0': {
    text: 'I have noticed some problems. But how do we know what is happening with the rain, soil, and crops?',
    replies: [
      { label: 'From space?', say: 'Can we see that from space?' },
      { label: 'Visit every farm?', say: 'Do we have to visit every farm?' },
      { label: 'The manual', say: 'Does the manual explain it?' },
    ],
  },
  '2-1': {
    text: 'There is a way to observe without visiting every farm. Let us use the eyes of space! Satellites can see vegetation, temperature, rain, and soil moisture.',
  },
  '2-2': {
    text: 'First, find Mozambique on the map. It is our country in this adventure.',
  },
  '2-3': {
    text: 'Now meet four tools. Each one observes a different part of Earth.',
  },
  '2-4': {
    text: 'Then we need to learn how to use each tool to help the community!',
    replies: [
      { label: 'Rain', say: 'I want to learn how to see the rain.' },
      { label: 'Heat', say: 'I want to learn how to see the heat.' },
      { label: 'Plants', say: 'I want to learn how to see the plants.' },
    ],
  },
  '2-5': {
    text: 'Mission 02 complete. The eyes of space are open. Next: the mystery of the rain.',
  },
  '3-0': {
    text: 'I have farmed this land for many years. We used to know when to plant. Now it is hard to tell when the rain will come.',
  },
  '3-1': {
    text: 'Some of the maize plants have curled leaves. The soil looks dry.',
    replies: [
      { label: 'The maize is struggling', say: 'The maize is struggling. Could there have been less rain?' },
      { label: 'Ask Ms. Amelia', say: 'Ms. Amelia, what should we do?' },
      { label: 'Open the manual', say: 'I will open the AgroSpace Manual.' },
    ],
  },
  '3-2': {
    text: 'New mission: The Rainfall Mystery. Investigate rainfall and help the community understand the risks for the next growing season.',
  },
  '3-3': {
    text: 'We will use NASA GPM — Global Precipitation Measurement. It measures rain and snow in many regions. Past data cannot guarantee future rain, but it can help us plan.',
  },
  '3-4': {
    text: 'Find the rainy season in this learning example. These are not real NASA data.',
  },
  '3-5': {
    text: 'If the reference rainfall was 700 mm and this fictional year had 490 mm, what was the decrease?',
  },
  '3-6': {
    text: 'If rainfall fell by 30%, will the crops die?',
    replies: [
      { label: 'Will they die?', say: 'Will all the crops die?' },
      { label: 'It depends', say: 'Maybe it depends on the soil and the crop.' },
      { label: 'Ask Ms. Amelia', say: 'Ms. Amelia, what do you think?' },
    ],
  },
  '3-7': {
    text: 'Not necessarily. The impact depends on when the rain was missing, the soil, and the crops. We need to look at how water is spread across the growing season.',
  },
  '3-8': {
    text: 'Some crops need water at certain times. If the rain fails then, we lose part of the harvest.',
  },
  '3-9': {
    text: 'The community expects little water. What is the best response?',
  },
  '3-10': {
    text: 'Science means asking good questions and bringing evidence together. Next: a heatwave.',
  },
  '4-0': {
    text: 'It is very hot today. The maize leaves look different. Could it be a disease?',
    replies: [
      { label: 'A disease?', say: 'Are the plants sick?' },
      { label: 'It is the heat', say: 'I think it is the heat.' },
      { label: 'Ms. Amelia', say: 'Ms. Amelia, what is happening?' },
    ],
  },
  '4-1': {
    text: 'It is not always a disease. Heat and lack of water can affect plants too. Talk to the astronaut.',
  },
  '4-2': {
    text: 'NASA POWER has arrived with temperature and solar energy data. We will look at the maximum, minimum, and average temperatures. Plants respond in different ways.',
  },
  '4-3': {
    text: 'Which day was the hottest in this example week?',
  },
  '4-4': {
    text: 'Heat can make a plant need more water. Without water, it closes its pores and grows less. Try the simulator.',
  },
  '4-5': {
    text: 'We do not have irrigation for every farm. What can we do?',
  },
  '4-6': {
    text: 'Compare practices before you decide.',
  },
  '4-7': {
    text: 'Next, we will look at the water that remains in the soil after rain. Two farms can get the same rain and still be different.',
  },
  '5-0': {
    text: 'It rained yesterday. I thought the plants would be doing better by now.',
    replies: [
      { label: 'It rained!', say: 'It rained! The soil must be wet now.' },
      { label: 'Still dry', say: 'That is strange: the surface is already drying out.' },
      { label: 'Look at the soil', say: 'Ms. Amelia, show me the soil.' },
    ],
  },
  '5-1': {
    text: 'Some water soaks in, some runs off, and some evaporates. We need to understand our farm.',
  },
  '5-2': {
    text: 'NASA SMAP observes moisture in the top 5 cm of soil across large areas. It cannot tell us exactly what is happening on your farm, so combine it with what you see in the field.',
  },
  '5-3': {
    text: 'Which area is driest at the surface?',
  },
  '5-4': {
    text: 'One hundred drops fell. Where did the water go?',
  },
  '5-5': {
    text: 'This layer of straw over the soil protects it from the sun and heavy rain.',
  },
  '5-6': {
    text: 'How can we conserve moisture with limited resources?',
  },
  '5-7': {
    text: 'Choose the right tool for each question.',
  },
  '5-8': {
    text: 'Next: the green signs of plants, seen from space.',
  },
  '6-0': {
    text: 'Some plants are green. Others are yellow. We need to investigate.',
  },
  '6-1': {
    text: 'Landsat measures the light reflected by Earth. We use red and near-infrared light to calculate NDVI — a sign of vegetation.',
  },
  '6-2': {
    text: 'Move the controls. When infrared is higher than red, NDVI goes up.',
  },
  '6-3': {
    text: 'Which area has the lowest NDVI?',
  },
  '6-4': {
    text: 'NDVI is down, rain is low, heat is high, and the soil is dry. What can we conclude?',
  },
  '6-5': {
    text: 'What should we do if the green signal has gone down?',
  },
  '6-6': {
    text: 'Choose the most careful decision.',
  },
  '6-7': {
    text: 'It is time to learn about the soil beneath our feet.',
  },
  '7-0': {
    text: 'In one place, the soil is loose and dark. In another, it is hard and cracked. Soil holds water, plant food, and life.',
  },
  '7-1': {
    text: 'Satellites see the surface. You need your eyes and hands to understand soil structure and nutrients.',
  },
  '7-2': {
    text: 'Explore sand, loam, and clay.',
  },
  '7-3': {
    text: 'Organic matter helps hold water and support life. Build soil that is protected.',
  },
  '7-4': {
    text: 'Do yellow leaves always mean the crop needs fertilizer?',
  },
  '7-5': {
    text: 'It could be a nutrient, water, or disease problem. First, meet the three friends: N, P, and K.',
  },
  '7-6': {
    text: 'Heavy rain washed soil down the slope!',
  },
  '7-7': {
    text: 'See how slope, ground cover, and rain change the risk.',
  },
  '7-8': {
    text: 'Keep a record of what you observed on the farm. We will need it when planning the rotation.',
  },
  '7-9': {
    text: 'Next: the Crop Academy. Maize, cowpea, sorghum, and groundnut.',
  },
  '8-0': {
    text: 'I grow maize, cowpea, and sorghum. This year I want to think more carefully about what to plant.',
  },
  '8-1': {
    text: 'No crop is best everywhere. Let us visit four gateways.',
  },
  '8-2': {
    text: 'Who am I? I am a legume, and some varieties can withstand heat and little rain.',
  },
  '8-3': {
    text: 'Choose a crop and a water level. This does not predict the harvest — it is only for learning.',
  },
  '8-4': {
    text: 'Legumes can fix nitrogen with the help of bacteria. The benefit to the next crop depends on how they are managed.',
  },
  '8-5': {
    text: 'We also need food, seeds, and some income from sales. Mark up to three priorities.',
  },
  '8-6': {
    text: 'Build a sequence for three growing seasons.',
  },
  '8-7': {
    text: 'Now for the big challenge: compare three strategies in the Rotation Lab.',
  },
  '9-0': {
    text: 'Maize feeds us. I do not want to give it up without understanding why. Let us compare three options.',
  },
  '9-1': {
    text: 'Four signs: GPM rainfall, POWER heat, SMAP moisture, and Landsat vegetation. They describe the environment — they cannot choose a crop rotation on their own.',
  },
  '9-2': {
    text: 'A: maize-maize-maize. B: maize-cowpea-sorghum. C: sorghum-cowpea-groundnut. Adjust what the community values.',
  },
  '9-3': {
    text: 'A high number with a lot of uncertainty can be risky.',
  },
  '9-4': {
    text: 'Before making a recommendation, we check seeds, soil, rain, food, the market, and a small trial.',
  },
  '9-5': {
    text: 'Which strategy do you want to investigate first? This is not a final order.',
  },
  '9-6': {
    text: 'The comparison has begun. Next, we test drought, heat, and heavy rain.',
  },
  '10-0': {
    text: 'What if the rain fails? Or what if it all comes at once?',
  },
  '10-1': {
    text: 'Welcome to the Storm Room. We test ideas without putting a real farm at risk.',
  },
  '10-2': {
    text: 'See how the three rotations change under each threat. These are game numbers, not real harvest figures.',
  },
  '10-3': {
    text: 'There is less and less water.',
  },
  '10-4': {
    text: 'What response should we investigate during a drought?',
  },
  '10-5': {
    text: 'Long periods of heat can affect flowering. What information should we use?',
  },
  '10-6': {
    text: 'The heavy rain is washing the soil away.',
  },
  '10-7': {
    text: 'How can we protect the farm?',
  },
  '10-8': {
    text: 'The final decision should take into account what the community can do. Next: the farmer’s choice.',
  },
  '11-0': {
    text: 'We have studied rain, heat, soil, plants, and crops. Now we choose what to try.',
  },
  '11-1': {
    text: 'The decision is yours. I can help you understand the evidence, costs, and what we still do not know.',
  },
  '11-2': {
    text: 'Tell environmental evidence apart from assumptions.',
  },
  '11-3': {
    text: 'When the ranges overlap, there is no clear winner.',
  },
  '11-4': {
    text: 'Before planting, we mark what we have already checked.',
  },
  '11-5': {
    text: 'Record your choice, the risks, and how you will test it in the field.',
  },
  '11-6': {
    text: 'The land matters. So do people. The final mission is the harvest.',
  },
  '12-0': {
    text: 'Harvest day has arrived. What if the strategy did not work?',
    replies: [
      { label: 'I am nervous', say: 'I am nervous about the results.' },
      { label: 'Let us see', say: 'Let us see what the land has taught us.' },
      { label: 'Ms. Amelia', say: 'Ms. Amelia, what have we learned, even if the harvest is small?' },
    ],
  },
  '12-1': {
    text: 'A farmer can learn from a difficult harvest too.',
  },
  '12-2': {
    text: 'Follow the four stages of the trial.',
  },
  '12-3': {
    text: 'Mark the sources you would use. Do not forget the field.',
  },
  '12-4': {
    text: 'Do not add up maize, cowpea, and groundnut as if they were the same thing. Change the prices and see how the story changes.',
  },
  '12-5': {
    text: 'Separate results from conclusions made too quickly.',
  },
  '12-6': {
    text: 'So which crop is best?',
  },
  '12-7': {
    text: 'The best choice depends on the place, the year, the water, the soil, and the people. What matters is asking good questions.',
  },
  '12-8': {
    text: 'Prepare the community’s legacy.',
  },
  '12-9': {
    text: 'AgroSpace is more than the spacecraft. It is what you have learned together. The next mission belongs to the community.',
  },
  '12-10': {
    text: 'Guardian of Earth and the Stars. The future of farming is not only among the stars. It is in the hands of those who care for the land.',
  },
}
