.. VELIGER - Editor de metadados documentation master file, created by
   sphinx-quickstart on Fri Mar 19 18:09:13 2010.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentação do editor de metadados VÉLIGER
===========================================

VÉLIGER é o editor de metadados do banco de imagens do Centro de Biologia
Marinha da Universidade de São Paulo (CEBIMar-USP).

Este programa abre imagens JPG, lê seus metadados (IPTC) e fornece uma
interface para editar estas informações. Os campos foram adaptados para o
propósito do banco, que é divulgar imagens com conteúdo biológico. Saiba mais
nos detalhes técnicos(link).

Os campos editáveis: título, legenda, marcadores, táxon, espécie, especialista,
autor, direitos, tamanho, local, cidade, estado e país.

Guia rápido
-----------

Instale o programa seguindo estas instruções (link em breve) e inicie-o.

Ao importar imagens o programa irá ler os metadados de cada uma e criar as
respectivas entradas na tabela principal. Selecione uma linha da tabela para
visualizar o thumbnail e os metadados contidos na imagem.

Para editar clique 2x na célula da tabela ou clique e aperte F2; após digitar
aperte *Enter* e o valor está salvo no programa (mas ainda não foi gravado na
imagem).

Outra maneira de editar é usando os campos de edição. Após selecionar uma
entrada na tabela os campos de edição serão preenchidos com os metadados da
imagem. Para editar simplesmente escreva as informações nos campos desejados e
aperte **ctrl+s** [#]_ antes de mudar para outra imagem. Caso você mude a linha
selecionada antes de salvar as alterações serão perdidas.

.. note::
    Lembre-se que salvar com ctrl+s, ou editando direto na tabela, não
    grava as alterações no arquivo da imagem. Os novos metadados ficam salvos
    apenas no programa, mas de maneira persistente (não é perdido após
    reiniciá-lo).

Após a alteração dos metadados a entrada é adicionada à uma lista que mostra os
arquivos cujos metadados foram modificados, mas ainda não foram gravados no
arquivo (ou seja, o arquivo ainda está com os metadados originais). Para gravar
os metadados na imagem utilize o atalho **ctrl+shift+s** [#]_. Se tudo correr
bem na gravação os novos metadados estarão embebidos na imagem.

.. note::
    A codificação utilizada para gravar os metadados é UTF-8. Veja mais
    informações sobre a codificação dos metadados abaixo.

Para editar várias entradas de uma vez selecione uma coluna de uma entrada e
arraste até outra entrada (ou clique e segure **shift** ou **ctrl** para
selecionar outras); com as entradas selecionadas aperte F2 e ele vai abrir o
campinho de edição na tabela; escreva e aperte *Enter* e os valores serão
copiados para as entradas selecionadas (apenas para a coluna escolhida).

Ao fechar o programa ele lembra a tabela e suas modificações, portanto pode
fechar sem apertar **Ctrl+Shift+S** que as modificações continuaram presentes
quando programa for aberto novamente.

.. [#] ou use o ícone para salvar no menu de ferramentas.
.. [#] ou clique em gravar na doca de modificadas.

Conversão da codificação
++++++++++++++++++++++++
Se você observar erros na codificação de caracteres especiais (ç, à, á, ã, ê)
dos metadados após importar imagens, o programa que inseriu estes dados deve
ter utilizado o padrão Latin-1 (ISO 8859-1). Para corrigir a codificação para o
padrão preferido atualmente, o UTF-8, utilize a função de conversão no menu
Editar. Essa alteração é gravada na imagem, logo, tenha backup sempre, pois se
você voltar a editar esta imagem com outro programa pode ser que ele não
reconheça o UTF-8 corretamente (acho difícil, mas pode acontecer).

Docas
+++++
A janela principal do **VÉLIGER** contém 3 docas: editor dos metadados,
miniatura da imagem e lista de entradas modificadas. Estas docas tem um
posicionamento padrão, mas podem ser modificados pelo usuário; são arrastáveis,
móveis e destacáveis.

Atalhos de teclado
------------------

Principais atalhos de teclado disponíveis:

============        =======================================================
Atalho              Função
============        =======================================================
ctrl+o              Importar arquivo(s) .jpg
ctrl+d              Importar recursivamente todo o conteúdo de uma pasta
ctrl+s              Salvar os metadados nos campos de edição para a tabela
ctrl+shift+s        Gravar os metadados alterados nas respectivas imagens
alt+[a-z]           Focar o cursor nos menus ou campos de edição
                    (e.g., alt+p colocará o cursor no campo **País**)
shift+e             Mostrar/esconder a doca com campos de edição
shift+t             Mostrar/esconder a doca com miniatura da imagem
shift+u             Mostrar/esconder a doca com lista de entradas modificadas
ctrl+q              Sair do programa
============        =======================================================

Algumas funções mais drásticas como limpar a tabela principal e converter a
codificação dos caracteres não tem atalhos para evitar acidentes.

Tópicos
-------
.. toctree::
    :maxdepth: 2

    API completa <fullapi>

Índices e tabelas
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

