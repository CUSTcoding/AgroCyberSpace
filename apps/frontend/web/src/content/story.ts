import type { Reply, Slide } from '../types'
import { go, line } from './helpers'

const ask = (a: Reply, b: Reply, c?: Reply): Reply[] => (c ? [a, b, c] : [a, b])

const m1: Slide[] = [
  line('1-0', 'space', 'narrator', 'Uma nave observa a Terra. Lá em baixo, uma comunidade agrícola em Moçambique precisa de ajuda com a chuva, o calor e o solo.'),
  line('1-1', 'space', 'astronaut', 'Recebi um sinal da Terra: a machamba está a sofrer. Vou aterrar junto da comunidade.'),
  line(
    '1-2',
    'village',
    'farmer',
    'Uma máquina caiu do céu! Quem será?',
    {
      replies: ask(
        { icon: '👋', label: 'Olá!', say: 'Olá! Quem és tu?' },
        { icon: '🚀', label: 'Essa máquina?', say: 'De onde vem essa máquina?' },
        { icon: '😮', label: 'Estou a ver', say: 'Nunca vi nada assim.' },
      ),
    },
  ),
  line('1-3', 'farm', 'astronaut', 'Venho do espaço. Estou numa missão para ajudar comunidades agrícolas a compreender o ambiente e a proteger as culturas.'),
  line(
    '1-4',
    'dry',
    'farmer',
    'Aqui temos muitos problemas.',
    {
      replies: ask(
        { icon: '🌧️', label: 'A chuva', say: 'Às vezes não sabemos quando vai chover.' },
        { icon: '🌱', label: 'As plantas', say: 'As nossas culturas não crescem como esperávamos.' },
        { icon: '🥵', label: 'O calor', say: 'O calor também está a prejudicar a terra.' },
      ),
    },
  ),
  line('1-5', 'ship', 'astronaut', 'É precisamente por isso que estou aqui. Trouxe o Manual de Missões AgroSpace.'),
  line('1-6', 'hologram', 'manual', 'Este manual é o teu guia. Cada missão ensina sobre clima, água, solo e culturas. Vais investigar e decidir.'),
  line(
    '1-7',
    'farm',
    'farmer',
    'Então este manual resolve todos os problemas?',
    {
      replies: ask(
        { icon: '📘', label: 'Mostra o manual', say: 'Mostra-me o manual.' },
        { icon: '🤔', label: 'Resolve tudo?', say: 'Este manual vai dizer-me como resolver todos os nossos problemas?' },
        { icon: '🤝', label: 'Vamos juntos', say: 'Quero aprender com a comunidade.' },
      ),
    },
  ),
  line('1-8', 'lab', 'astronaut', 'Vai ajudar-te a encontrar respostas. Mas terás de investigar. Nem todas as soluções funcionam em todas as machambas.'),
  line('1-9', 'night', 'narrator', 'Missão 01 concluída. O agricultor, o astronauta e a comunidade começam a aventura AgroSpace.'),
]

const m2: Slide[] = [
  line('2-0', 'ship', 'farmer', 'Já vi alguns problemas. Mas como sabemos o que acontece com a chuva, o solo e as culturas?', {
    replies: ask(
      { icon: '🛰️', label: 'Do espaço?', say: 'Conseguimos ver isso do espaço?' },
      { icon: '🚶', label: 'Visitar tudo?', say: 'Temos de visitar todas as machambas?' },
      { icon: '📘', label: 'O manual', say: 'O manual explica?' },
    ),
  }),
  line('2-1', 'hologram', 'astronaut', 'Há uma maneira de observar sem visitar todas as machambas. Vamos usar os olhos do espaço! Os satélites vêem vegetação, temperatura, chuva e humidade do solo.'),
  line('2-2', 'hologram', 'astronaut', 'Primeiro, encontra Moçambique no mapa. É o nosso país nesta aventura.', {
    challenge: { type: 'mz-map' },
    replies: go,
  }),
  line('2-3', 'lab', 'astronaut', 'Agora conhece quatro ferramentas. Cada uma observa uma parte diferente da Terra.', {
    challenge: { type: 'tools' },
  }),
  line('2-4', 'farm', 'farmer', 'Então precisamos de aprender a usar cada uma para ajudar a comunidade!', {
    replies: ask(
      { icon: '🌧️', label: 'Chuva', say: 'Quero aprender a ver a chuva.' },
      { icon: '🌡️', label: 'Calor', say: 'Quero aprender a ver o calor.' },
      { icon: '🌿', label: 'Plantas', say: 'Quero aprender a ver as plantas.' },
    ),
  }),
  line('2-5', 'night', 'narrator', 'Missão 02 concluída. Os olhos do espaço estão abertos. A seguir: o mistério da chuva.'),
]

const m3: Slide[] = [
  line('3-0', 'dry', 'amelia', 'Há muitos anos cultivo nesta terra. Antes sabíamos quando semear. Agora é difícil saber quando vem a chuva.'),
  line('3-1', 'dry', 'farmer', 'Algumas plantas de milho estão enroladas. O solo parece seco.', {
    replies: ask(
      { icon: '🌽', label: 'O milho sofre', say: 'O milho está a sofrer. Será que choveu menos?' },
      { icon: '👵', label: 'Ouvir Dona Amélia', say: 'Dona Amélia, o que devemos fazer?' },
      { icon: '📘', label: 'Abrir o manual', say: 'Vou abrir o Manual AgroSpace.' },
    ),
  }),
  line('3-2', 'hologram', 'manual', 'Nova missão: The Rainfall Mystery. Investiga as chuvas e ajuda a comunidade a compreender os riscos da próxima campanha.'),
  line('3-3', 'ship', 'astronaut', 'Vamos usar a NASA GPM — Global Precipitation Measurement. Mede chuva e neve em muitas regiões. Os dados históricos não garantem a próxima chuva, mas ajudam a planear.'),
  line('3-4', 'lab', 'astronaut', 'Descobre a estação chuvosa neste exemplo didático. Não são dados reais da NASA.', {
    challenge: {
      type: 'quiz',
      question: 'Qual é o período com mais chuva neste desenho?',
      options: [
        { icon: '🌧️', label: 'Dezembro a Março', correct: true },
        { icon: '☀️', label: 'Maio a Agosto' },
        { icon: '❄️', label: 'Junho a Setembro' },
      ],
    },
  }),
  line('3-5', 'lab', 'astronaut', 'Se a chuva de referência era 700 mm e este ano fictício teve 490 mm, qual foi a redução?', {
    challenge: {
      type: 'quiz',
      question: 'A chuva baixou de 700 para 490. Qual a redução?',
      options: [
        { icon: '2️⃣', label: '20%' },
        { icon: '3️⃣', label: '30%', correct: true },
        { icon: '6️⃣', label: '60%' },
      ],
    },
  }),
  line('3-6', 'village', 'farmer', 'Se a chuva diminuiu 30%, as culturas vão morrer?', {
    replies: ask(
      { icon: '😱', label: 'Vão morrer?', say: 'Todas as culturas vão morrer?' },
      { icon: '🧠', label: 'Depende', say: 'Talvez dependa da terra e da cultura.' },
      { icon: '👵', label: 'Perguntar à Dona Amélia', say: 'Dona Amélia, o que acha?' },
    ),
  }),
  line('3-7', 'farm', 'astronaut', 'Não necessariamente. O impacto depende de quando faltou a chuva, do solo e das culturas. Precisamos de ver a distribuição da água no ciclo.'),
  line('3-8', 'council', 'amelia', 'Algumas culturas precisam de água em momentos certos. Se a chuva falhar nessa altura, perdemos parte da produção.'),
  line('3-9', 'dry', 'astronaut', 'A comunidade espera pouca água. Qual é a melhor resposta?', {
    challenge: {
      type: 'quiz',
      question: 'Como reduzir o risco com pouca água?',
      options: [
        { icon: '🙈', label: 'Não mudar nada' },
        { icon: '🔍', label: 'Analisar culturas e conservar humidade', correct: true },
        { icon: '🚿', label: 'Irrigar sem ver se há água' },
      ],
    },
  }),
  line('3-10', 'night', 'astronaut', 'A ciência é fazer boas perguntas e juntar evidências. A seguir: uma onda de calor.'),
]

const m4: Slide[] = [
  line('4-0', 'heat', 'farmer', 'Hoje está muito quente. As folhas do milho parecem diferentes. Será doença?', {
    replies: ask(
      { icon: '🤒', label: 'Doença?', say: 'As plantas estão doentes?' },
      { icon: '☀️', label: 'É o calor', say: 'Acho que é o calor.' },
      { icon: '👵', label: 'Dona Amélia', say: 'Dona Amélia, o que está a acontecer?' },
    ),
  }),
  line('4-1', 'heat', 'amelia', 'Nem sempre é doença. O calor e a falta de água também afetam as plantas. Fala com o astronauta.'),
  line('4-2', 'ship', 'astronaut', 'Chegou a NASA POWER: dados de temperatura e energia solar. Vamos ver máxima, mínima e média. As plantas reagem de formas diferentes.'),
  line('4-3', 'lab', 'astronaut', 'Qual foi o dia mais quente desta semana fictícia?', {
    challenge: {
      type: 'quiz',
      question: 'Dia mais quente da semana de exemplo',
      options: [
        { icon: '🌤️', label: 'Quarta — 35°C' },
        { icon: '🔥', label: 'Sexta — 40°C', correct: true },
        { icon: '☀️', label: 'Domingo — 34°C' },
      ],
    },
  }),
  line('4-4', 'heat', 'astronaut', 'O calor pode fazer a planta pedir mais água. Sem água, ela fecha os estomas e cresce menos. Experimenta o simulador.', {
    challenge: { type: 'plant-sim' },
  }),
  line('4-5', 'village', 'amelia', 'Não temos irrigação para todas as machambas. O que podemos fazer?'),
  line('4-6', 'farm', 'astronaut', 'Compara práticas antes de decidir.', {
    challenge: {
      type: 'quiz',
      question: 'Qual estratégia investigar primeiro?',
      options: [
        { icon: '🙈', label: 'Não acompanhar o calor' },
        { icon: '🪵', label: 'Cobertura do solo e culturas adaptadas', correct: true },
        { icon: '🚿', label: 'Irrigar sem ver o custo da água' },
      ],
    },
  }),
  line('4-7', 'night', 'astronaut', 'A seguir vamos ver a água que fica no solo depois da chuva. Duas machambas podem receber a mesma chuva e ficar diferentes.'),
]

const m5: Slide[] = [
  line('5-0', 'rain', 'farmer', 'Ontem choveu. Pensei que as plantas já estivessem melhor.', {
    replies: ask(
      { icon: '🌧️', label: 'Choveu!', say: 'Choveu! A terra já deve estar molhada.' },
      { icon: '😮', label: 'Continua seca', say: 'Estranho: a superfície já está a secar.' },
      { icon: '👵', label: 'Ver a terra', say: 'Dona Amélia, mostra-me a terra.' },
    ),
  }),
  line('5-1', 'soil', 'amelia', 'Parte da água infiltra, parte escorre, parte evapora. Precisamos de compreender a nossa machamba.'),
  line('5-2', 'ship', 'astronaut', 'NASA SMAP observa a humidade nos primeiros 5 cm do solo, em áreas grandes. Não diz exatamente a tua machamba — junta com o que vês no terreno.'),
  line('5-3', 'lab', 'astronaut', 'Qual zona está mais seca à superfície?', {
    challenge: { type: 'moisture-zones' },
  }),
  line('5-4', 'rain', 'astronaut', 'Cairam 100 gotas. Para onde foi a água?', {
    challenge: { type: 'water-split' },
  }),
  line('5-5', 'farm', 'amelia', 'Esta palha sobre a terra protege do sol e da chuva forte.'),
  line('5-6', 'soil', 'astronaut', 'Como conservar a humidade com recursos limitados?', {
    challenge: {
      type: 'quiz',
      question: 'Como guardar a água no solo?',
      options: [
        { icon: '🏜️', label: 'Deixar o solo nu' },
        { icon: '🪵', label: 'Cobertura morta com restos das plantas', correct: true },
        { icon: '🚿', label: 'Irrigar sem ver se há água' },
      ],
    },
  }),
  line('5-7', 'lab', 'astronaut', 'Escolhe a ferramenta certa para cada pergunta.', {
    challenge: {
      type: 'multi-quiz',
      questions: [
        {
          question: 'Tendências regionais da humidade superficial?',
          options: [
            { icon: '🛰️', label: 'NASA SMAP', correct: true },
            { icon: '📷', label: 'Só uma foto da machamba' },
            { icon: '🌡️', label: 'Temperatura de um dia' },
          ],
        },
        {
          question: 'Saber se A TUA machamba está molhada?',
          options: [
            { icon: '✋', label: 'Ver e medir no terreno', correct: true },
            { icon: '🛰️', label: 'Só o satélite, sem ir ao campo' },
            { icon: '🎲', label: 'Adivinhar' },
          ],
        },
        {
          question: 'O SMAP mede a água nas raízes profundas?',
          options: [
            { icon: '✅', label: 'Sim, tudo' },
            { icon: '5️⃣', label: 'Não; mede sobretudo os primeiros 5 cm', correct: true },
            { icon: '🌊', label: 'Só rios' },
          ],
        },
      ],
    },
  }),
  line('5-8', 'night', 'astronaut', 'A seguir: os sinais verdes das plantas, vistos do espaço.'),
]

const m6: Slide[] = [
  line('6-0', 'farm', 'amelia', 'Algumas plantas estão verdes. Outras amarelas. Precisamos de investigar.'),
  line('6-1', 'hologram', 'astronaut', 'O Landsat mede a luz que a Terra devolve. Com vermelho e infravermelho próximo calculamos o NDVI — um sinal da vegetação.'),
  line('6-2', 'lab', 'astronaut', 'Mexa nos controlos. Quando o infravermelho é maior que o vermelho, o NDVI sobe.', {
    challenge: { type: 'ndvi' },
  }),
  line('6-3', 'hologram', 'astronaut', 'Qual zona tem o menor NDVI?', {
    challenge: { type: 'ndvi-map' },
  }),
  line('6-4', 'dry', 'astronaut', 'NDVI baixou, chuva fraca, calor alto, solo seco. Qual conclusão?', {
    challenge: {
      type: 'quiz',
      question: 'O que os sinais dizem?',
      options: [
        { icon: '❌', label: 'É só seca, com certeza' },
        { icon: '🔍', label: 'Pode ser água ou calor — precisamos ver no campo', correct: true },
        { icon: '🦠', label: 'O NDVI prova uma doença' },
      ],
    },
  }),
  line('6-5', 'farm', 'amelia', 'O que fazer se o sinal verde diminuiu?'),
  line('6-6', 'farm', 'astronaut', 'Escolhe a decisão mais cuidadosa.', {
    challenge: {
      type: 'quiz',
      question: 'O NDVI baixou. E agora?',
      options: [
        { icon: '🧪', label: 'Deitar adubo já, sem ver o solo' },
        { icon: '👀', label: 'Ver a cultura, os dados e o terreno', correct: true },
        { icon: '🚪', label: 'Abandonar a machamba' },
      ],
    },
  }),
  line('6-7', 'night', 'amelia', 'Chegou a hora de conhecer a terra debaixo dos nossos pés.'),
]

const m7: Slide[] = [
  line('7-0', 'soil', 'amelia', 'Num sítio o solo está solto e escuro. Noutro está duro e com fendas. A terra guarda água, comida das plantas e vida.'),
  line('7-1', 'lab', 'astronaut', 'Os satélites vêem a superfície. A estrutura e os nutrientes precisam dos teus olhos e das tuas mãos.'),
  line('7-2', 'soil', 'astronaut', 'Explora areia, franco e argila.', {
    challenge: { type: 'soil-texture' },
  }),
  line('7-3', 'farm', 'astronaut', 'A matéria orgânica ajuda a guardar água e vida. Constrói um solo protegido.', {
    challenge: { type: 'practices' },
  }),
  line('7-4', 'lab', 'amelia', 'Folhas amarelas querem sempre adubo?'),
  line('7-5', 'lab', 'astronaut', 'Pode ser nutriente, água ou doença. Primeiro os três amigos: N, P e K.', {
    challenge: {
      type: 'multi-quiz',
      questions: [
        {
          question: 'Qual nutriente ajuda o crescimento verde e as proteínas?',
          options: [
            { icon: '🇳', label: 'Azoto (N)', correct: true },
            { icon: '🇰', label: 'Potássio (K)' },
            { icon: '🦴', label: 'Cálcio (Ca)' },
          ],
        },
        {
          question: 'Qual ajuda a planta a gerir a água?',
          options: [
            { icon: '🇳', label: 'Azoto (N)' },
            { icon: '🇰', label: 'Potássio (K)', correct: true },
            { icon: '☀️', label: 'Só o sol' },
          ],
        },
        {
          question: 'Qual está ligado à energia da planta?',
          options: [
            { icon: '🇵', label: 'Fósforo (P)', correct: true },
            { icon: '💨', label: 'Vento' },
            { icon: '🪨', label: 'Pedras' },
          ],
        },
      ],
    },
  }),
  line('7-6', 'rain', 'amelia', 'A chuva forte levou terra encosta abaixo!'),
  line('7-7', 'storm', 'astronaut', 'Vê como o declive, a cobertura e a chuva mudam o risco.', {
    challenge: { type: 'erosion' },
  }),
  line('7-8', 'council', 'astronaut', 'Guarda o que viste da machamba. Vamos precisar disto na rotação.', {
    challenge: { type: 'notebook' },
  }),
  line('7-9', 'night', 'amelia', 'A seguir: a Academia das Culturas. Milho, nhemba, sorgo e amendoim.'),
]

const m8: Slide[] = [
  line('8-0', 'village', 'amelia', 'Tenho milho, feijão-nhemba e sorgo. Este ano quero pensar melhor no que plantar.'),
  line('8-1', 'academy', 'astronaut', 'Nenhuma cultura é a melhor em todo o lado. Vamos conhecer quatro portais.'),
  line('8-2', 'academy', 'astronaut', 'Quem sou eu? Sou leguminosa e algumas variedades aguentam calor e pouca chuva.', {
    challenge: {
      type: 'quiz',
      question: 'Quem sou eu?',
      options: [
        { icon: '🌽', label: 'Milho' },
        { icon: '🫘', label: 'Feijão-nhemba', correct: true },
        { icon: '🌾', label: 'Sorgo' },
      ],
    },
  }),
  line('8-3', 'dry', 'astronaut', 'Escolhe uma cultura e um nível de água. Isto não prevê colheita — só ensina.', {
    challenge: { type: 'crop-water' },
  }),
  line('8-4', 'academy', 'astronaut', 'As leguminosas podem fixar azoto com bactérias. O benefício para a cultura seguinte depende da gestão.', {
    challenge: {
      type: 'quiz',
      question: 'O que é verdade sobre as leguminosas?',
      options: [
        { icon: '❌', label: 'Dão sempre todo o azoto ao milho' },
        { icon: '🌱', label: 'Podem fixar azoto; o benefício depende', correct: true },
        { icon: '🚫', label: 'Nunca ajudam o azoto' },
      ],
    },
  }),
  line('8-5', 'council', 'amelia', 'Também precisamos de comida, sementes e alguma venda. Marca até 3 prioridades.', {
    challenge: { type: 'priorities' },
  }),
  line('8-6', 'lab', 'astronaut', 'Monta uma sequência de 3 campanhas.', {
    challenge: { type: 'rotation-build' },
  }),
  line('8-7', 'night', 'astronaut', 'Agora o grande desafio: comparar três estratégias no Laboratório da Rotação.'),
]

const m9: Slide[] = [
  line('9-0', 'council', 'amelia', 'O milho alimenta-nos. Não o quero abandonar sem compreender. Vamos comparar três caminhos.'),
  line('9-1', 'lab', 'astronaut', 'Quatro sinais: chuva GPM, calor POWER, humidade SMAP, vegetação Landsat. Eles descrevem o ambiente — não escolhem a rotação sozinhos.', {
    challenge: { type: 'climate-lab' },
  }),
  line('9-2', 'hologram', 'astronaut', 'A: milho-milho-milho. B: milho-nhemba-sorgo. C: sorgo-nhemba-amendoim. Ajusta o que a comunidade valoriza.', {
    challenge: { type: 'rotation-compare' },
  }),
  line('9-3', 'lab', 'astronaut', 'Um número alto com grande incerteza pode ser arriscado.', {
    challenge: { type: 'uncertainty' },
  }),
  line('9-4', 'council', 'amelia', 'Antes de recomendar, verificamos sementes, solo, chuva, comida, mercado e um ensaio pequeno.', {
    challenge: {
      type: 'checklist',
      items: [
        { icon: '🌰', label: 'Sementes e custo' },
        { icon: '🧱', label: 'Solo e drenagem' },
        { icon: '🌧️', label: 'Calendário da chuva' },
        { icon: '🍲', label: 'Comida da família' },
        { icon: '🛒', label: 'Venda e arrumo' },
        { icon: '🧪', label: 'Ensaio pequeno' },
      ],
    },
  }),
  line('9-5', 'farm', 'astronaut', 'Qual estratégia queres investigar primeiro? Não é uma ordem final.', {
    challenge: { type: 'pick-strategy' },
  }),
  line('9-6', 'night', 'astronaut', 'A comparação começou. A seguir testamos seca, calor e chuva intensa.'),
]

const m10: Slide[] = [
  line('10-0', 'storm', 'amelia', 'E se a chuva falhar? Ou se vier toda de uma vez?'),
  line('10-1', 'ship', 'astronaut', 'Bem-vindos à Sala das Tempestades. Testamos hipóteses sem arriscar a machamba real.', {
    challenge: { type: 'extreme-sim' },
  }),
  line('10-2', 'lab', 'astronaut', 'Vê como as três rotações mudam em cada ameaça. Os números são de jogo, não de colheita real.', {
    challenge: { type: 'resilience' },
  }),
  line('10-3', 'dry', 'amelia', 'A água está a ficar pouca.'),
  line('10-4', 'dry', 'astronaut', 'Qual resposta investigar na seca?', {
    challenge: {
      type: 'quiz',
      question: 'Seca: o que fazer primeiro?',
      options: [
        { icon: '🙈', label: 'Não avaliar a água' },
        { icon: '🪵', label: 'Ver humidade, cobrir o solo, datas e variedades', correct: true },
        { icon: '🚿', label: 'Irrigar sem saber se há água' },
      ],
    },
  }),
  line('10-5', 'heat', 'astronaut', 'O calor longo pode afetar a floração. Que informação usar?', {
    challenge: {
      type: 'quiz',
      question: 'Antes de proteger do calor, o que olhar?',
      options: [
        { icon: '1️⃣', label: 'Só a máxima de um dia' },
        { icon: '📅', label: 'Duração, fase da planta, água e variedade', correct: true },
        { icon: '🛰️', label: 'Só uma imagem NDVI' },
      ],
    },
  }),
  line('10-6', 'rain', 'amelia', 'A chuva forte está a levar a terra.'),
  line('10-7', 'storm', 'astronaut', 'Como defender a machamba?', {
    challenge: {
      type: 'quiz',
      question: 'Chuva intensa: o que investigar?',
      options: [
        { icon: '🧹', label: 'Tirar toda a cobertura' },
        { icon: '🛡️', label: 'Cobertura, drenagem e conservação', correct: true },
        { icon: '🎉', label: 'Ignorar: chuva é sempre boa' },
      ],
    },
  }),
  line('10-8', 'night', 'amelia', 'A decisão final deve considerar o que a comunidade consegue fazer. A seguir: a escolha do agricultor.'),
]

const m11: Slide[] = [
  line('11-0', 'council', 'amelia', 'Já estudámos chuva, calor, solo, plantas e culturas. Agora escolhemos o que experimentar.'),
  line('11-1', 'lab', 'astronaut', 'A decisão é vossa. Eu ajudo a ler evidências, custos e o que ainda não sabemos.', {
    challenge: { type: 'rotation-compare' },
  }),
  line('11-2', 'hologram', 'astronaut', 'Distingue evidência ambiental de suposição.', {
    challenge: {
      type: 'multi-quiz',
      questions: [
        {
          question: 'O GPM ajuda a ver quando choveu?',
          options: [
            { icon: '✅', label: 'Sim', correct: true },
            { icon: '❌', label: 'Não' },
          ],
        },
        {
          question: 'O SMAP mede a água exacta das raízes da tua parcela?',
          options: [
            { icon: '✅', label: 'Sim, exacto' },
            { icon: '❌', label: 'Não; é regional e superficial', correct: true },
          ],
        },
        {
          question: 'O NDVI sozinho prova a melhor rotação?',
          options: [
            { icon: '✅', label: 'Sim' },
            { icon: '❌', label: 'Não', correct: true },
          ],
        },
        {
          question: 'A experiência da comunidade conta?',
          options: [
            { icon: '✅', label: 'Sim, muito', correct: true },
            { icon: '❌', label: 'Não' },
          ],
        },
      ],
    },
  }),
  line('11-3', 'lab', 'astronaut', 'Quando os intervalos se sobrepõem, ninguém é vencedor seguro.', {
    challenge: { type: 'uncertainty' },
  }),
  line('11-4', 'council', 'amelia', 'Antes de plantar, marcamos o que já verificámos.', {
    challenge: {
      type: 'checklist',
      items: [
        { icon: '🌰', label: 'Sementes' },
        { icon: '🧱', label: 'Solo' },
        { icon: '🌧️', label: 'Chuva' },
        { icon: '🍲', label: 'Comida' },
        { icon: '🛒', label: 'Mercado' },
        { icon: '🧪', label: 'Ensaio' },
      ],
    },
  }),
  line('11-5', 'farm', 'astronaut', 'Regista a tua escolha, os riscos e como vais testar no terreno.', {
    challenge: { type: 'report' },
  }),
  line('11-6', 'night', 'amelia', 'A terra é importante. As pessoas também. A última missão: a colheita.'),
]

const m12: Slide[] = [
  line('12-0', 'harvest', 'farmer', 'Chegou o dia da colheita. E se a estratégia não tiver funcionado?', {
    replies: ask(
      { icon: '😬', label: 'Estou nervoso', say: 'Estou nervoso com os resultados.' },
      { icon: '💪', label: 'Vamos ver', say: 'Vamos ver o que a terra nos ensinou.' },
      { icon: '👵', label: 'Dona Amélia', say: 'Dona Amélia, o que aprendemos mesmo que a colheita seja pouca?' },
    ),
  }),
  line('12-1', 'harvest', 'amelia', 'Um agricultor também aprende com uma colheita difícil.'),
  line('12-2', 'farm', 'astronaut', 'Acompanha as quatro fases do ensaio.', {
    challenge: { type: 'timeline' },
  }),
  line('12-3', 'hologram', 'astronaut', 'Marca as fontes que usarias. Não te esqueças do terreno.', {
    challenge: { type: 'sources' },
  }),
  line('12-4', 'lab', 'astronaut', 'Não somes milho, nhemba e amendoim como se fossem a mesma coisa. Mexe nos preços e vê a história mudar.', {
    challenge: { type: 'harvest-econ' },
  }),
  line('12-5', 'council', 'astronaut', 'Separa resultado de conclusão precipitada.', {
    challenge: {
      type: 'multi-quiz',
      questions: [
        {
          question: 'NDVI alto prova mais comida?',
          options: [
            { icon: '✅', label: 'Sim, sempre' },
            { icon: '❌', label: 'Não; é preciso medir a colheita', correct: true },
            { icon: '🌧️', label: 'Sim, se chover' },
          ],
        },
        {
          question: 'Uma campanha boa prova a rotação para sempre?',
          options: [
            { icon: '✅', label: 'Sim' },
            { icon: '❌', label: 'Não; o ano seguinte pode ser diferente', correct: true },
          ],
        },
        {
          question: 'Os dados da NASA substituem o agricultor?',
          options: [
            { icon: '✅', label: 'Sim' },
            { icon: '❌', label: 'Não; apoiam a decisão', correct: true },
          ],
        },
      ],
    },
  }),
  line('12-6', 'village', 'child', 'Então qual é a melhor cultura?'),
  line('12-7', 'village', 'amelia', 'A melhor escolha depende do lugar, do ano, da água, da terra e das pessoas. O importante é fazer boas perguntas.'),
  line('12-8', 'council', 'astronaut', 'Prepara o legado da comunidade.', {
    challenge: { type: 'report' },
  }),
  line('12-9', 'night', 'astronaut', 'O AgroSpace não é só a nave. É o que vocês aprenderam juntos. A próxima missão pertence à comunidade.'),
  line('12-10', 'harvest', 'narrator', 'Guardião da Terra e das Estrelas. O futuro da agricultura não está apenas nas estrelas. Está nas mãos de quem cuida da terra.'),
]

export const STORY: Record<number, Slide[]> = {
  1: m1,
  2: m2,
  3: m3,
  4: m4,
  5: m5,
  6: m6,
  7: m7,
  8: m8,
  9: m9,
  10: m10,
  11: m11,
  12: m12,
}
