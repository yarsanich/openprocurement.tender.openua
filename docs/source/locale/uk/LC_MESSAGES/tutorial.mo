��    V      �      |      |  ,   }  l   �       ?   +  :   k     �     �     �  0   �  #     =   %  m   c  ,   �     �  4     >   E     �     �  	   �  :   �  8   �  G   +	     s	  >   �	  B   �	  �   
  X   �
  X      N   Y  /   �  #   �  S   �  8   P  +   �  -   �  ,   �  L        ]  *   }     �  '   �  '   �  �   	  �   �     7  "   U  !   x  �   �  '     o   F     �  G   �       3   !  t   U     �      �  u        �  �  �  P   \  ?   �  6   �  �   $  W   	  /   a  �   �  z   !     �  "   �     �      �       :     �   U  �     �   �  6   ;  ;   r  9   �  D   �  �   -  W   �  F   +     r    �  L   �  �   �  %   �  j      ]   n      �   /   �   0   !  s   <!  S   �!  �   "  �   �"  K   }#  '   �#  Q   �#  l   C$  3   �$  %   �$  (   
%  �   3%  P   �%  p   &     x&  \   �&  k   �&    ]'  �   x(  �   3)  �   �)  J   o*  9   �*  u   �*  @   j+  <   �+  L   �+  H   5,  �   ~,  3    -  b   4-  )   �-  @   �-  :   .  6  =.  "  t/  :   �0  ;   �0  ;   1  �   J1  p   ?2  �   �2  -   ~3  U   �3  )   4     ,4  �   �4  A   `5  9   �5    �5  4   �6  �  '7  �   :  j   �:  w   <;  =  �;  �   �<  j   �=  9  >  �   @?     �?  ?   @  ,   A@  A   n@  -   �@  g   �@    FA  %  [B  r  �C  e   �D  �   ZE  ]   �E  o   :F  8  �F  �   �G  �   wH  '   I   Activating the request and cancelling tender After auction is scheduled anybody can visit it to watch. The auction can be reached at `Tender.auctionUrl`: And activate a bid: And again we can confirm that there are two documents uploaded. And we can see that it is overriding the original version: Auction Bid confirmation Bid invalidation Bidder can register a bid with ``draft`` status: Bidder should confirm bid proposal: Bidders can find out their participation URLs via their bids: By default contract value is set based on the award, but there is a possibility to set custom contract value. Cancel the tender with the prepared reasons. Cancelling tender Change the document description and other properties Checking the listing again reflects the new modification date: Confirming qualification Creating tender Enquiries Enquiries can be made only during ``Tender.enqueryPeriod`` Error states that no `data` has been found in JSON body. Error states that the only accepted Content-Type is `application/json`. Exploring basic rules Fill it with the protocol describing the cancellation reasons. Filling cancellation with protocol and supplementary documentation If tender is modified, status of all bid proposals will be changed to ``invalid``. Bid proposal will look the following way after tender has been modified: If this date is not set, it will be auto-generated on the date of contract registration. If you want to **lower contract value**, you can insert new one into the `amount` field. In case we made an error, we can reupload the document over the older version: It is possible to check the uploaded documents: Just invoking it reveals empty set. Let's access the URL of the created object (the `Location` header of the response): Let's provide the data attribute in the submitted body : Let's satisfy the Content-type requirement: Let's see what listing of tenders reveals us: Let's try exploring the `/tenders` endpoint: Let's update tender by supplementing it with all other essential properties: Let's upload contract document: Let's view the uploaded contract document: Modifying tender Now let's attempt creating some tender: One can retrieve either questions list: Only the request that has been activated (3rd step above) has power to cancel tender.  I.e.  you have to not only prepare cancellation request but to activate it as well. Open UA procedure demands at least two bidders, so there should be at least two bid proposals registered to move to auction stage: Prepare cancellation request. Preparing the cancellation request Procuring entity can answer them: Procuring entity can not change tender if there are less than 7 days before tenderPeriod ends. Changes will not be accepted by API. Procuring entity can set bid guarantee: Procuring entity can upload PDF files into the created tender. Uploading should follow the :ref:`upload` rules. Proposal Uploading Qualification commission registers its decision via the following call: Registering bid See :ref:`cancellation` data structure for details. See the `Bid.participationUrl` in the response. Similar, but different, URL can be retrieved for other participants: Setting contract signature date Setting contract validity period Setting contract validity period is optional, but if it is needed, you can set appropriate `startDate` and `endDate`. Setting contract value Success! Now we can see that new object was created. Response code is `201` and `Location` response header reports the location of the created object.  The body of response reveals the information about the created tender: its internal `id` (that matches the `Location` segment), its official `tenderID` and `dateModified` datestamp stating the moment in time when tender was last modified.  Note that tender is created with `active.tendering` status. Tender creator can cancel tender anytime. The following steps should be applied: Tender status ``active.tendering`` allows registration of bids. That is why tenderPeriod has to be extended by 7 days. The peculiarity of the Open UA procedure is that ``procurementMethodType`` was changed from ``belowThreshold`` to ``aboveThresholdUA``. Also there is no opportunity to set up ``enquiryPeriod``, it will be assigned automatically. The single array element describes the uploaded document. We can upload more documents: Then bidder should upload proposal document(s): There are two possible types of cancellation reason - tender was `cancelled` or `unsuccessful`. By default ``reasonType`` value is `cancelled`. There is a possibility to set custom contract signature date. You can insert appropriate date into the `dateSigned` field. Tutorial Upload new version of the document Upload the file contents Uploading contract documentation Uploading documentation We can see the same response we got after creating tender. We do see the internal `id` of a tender (that can be used to construct full URL by prepending `http://api-sandbox.openprocurement.org/api/0/tenders/`) and its `dateModified` datestamp. We see the added properies have merged with existing tender data. Additionally, the `dateModified` property was updated to reflect the last modification datestamp. When tender has ``active.tendering`` status and ``Tender.enqueryPeriod.endDate``  hasn't come yet, interested parties can ask questions: You can change ``reasonType`` value to `unsuccessful`. You can upload contract documents for the OpenUA procedure. You should pass `reason`, `status` defaults to `pending`. `200 OK` response was returned. The value was modified successfully. `201 Created` response code and `Location` header confirm document creation. We can additionally query the `documents` collection API endpoint to confirm the action: `201 Created` response code and `Location` header confirm that this document was added. `id` is autogenerated and passed in the `Location` header of response. or individual answer: Project-Id-Version: openprocurement.tender.openua 0.1
Report-Msgid-Bugs-To: 
POT-Creation-Date: 2016-01-27 13:38+0200
PO-Revision-Date: 2016-06-13 13:01+0200
Last-Translator: sorenabell <sorenabell@quintagroup.com>
Language-Team: Ukrainian <support@quintagroup.com>
MIME-Version: 1.0
Content-Type: text/plain; charset=UTF-8
Content-Transfer-Encoding: 8bit
Language: uk
Plural-Forms: nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2);
Generated-By: Babel 2.2.0
X-Generator: Lokalize 2.0
 Активація запиту та скасування закупівлі Після того, як аукціон заплановано, будь-хто може його відвідати для перегляду. Аукціон можна подивитись за допомогою `Tender.auctionUrl`: І активувати ставку: І знову можна перевірити, що є два завантажених документа. І ми бачимо, що вона перекриває оригінальну версію: Аукціон Підтвердження пропозиції Пропозиція стає недійсною Учасник може зареєструвати ставку із статусом ``draft`` (чернетка): Учасник повинен підтвердити свою пропозицію: Учасники можуть дізнатись свої URL-адреси для участі через свої пропозиції: За замовчуванням вартість угоди встановлюється на основі рішення про визначення переможця, але є можливість змінити це значення.  Скасуйте закупівлю через подані причини. Скасування закупівлі Зміна опису документа та інших властивостей Ще одна перевірка списку відображає нову дату модифікації: Підтвердження кваліфікації Створення закупівлі Уточнення і запитання Запитання можна задавати лише протягом періоду уточнень ``Tender.enqueryPeriod``. Помилка вказує, що `data` не знайдено у тілі JSON. Помилка вказує, що єдиний прийнятний тип вмісту це `application/json`. Базові правила Наповніть його протоколом про причини скасування. Наповнення протоколом та іншою супровідною документацією Якщо закупівля була модифікована, статус всіх пропозицій змінюється на ``invalid`` (недійсний). Ось так пропозиція буде виглядати після редагування закупівлі: Якщо ви не встановите дату підписання, то вона буде згенерована автоматично під час реєстрації угоди. Якщо ви хочете **знизити вартість угоди**, ви можете встановити нове значення для поля `amount`. Якщо сталась помилка, ми можемо ще раз завантажити документ поверх старої версії: Можна перевірити завантажені документи: При виклику видає пустий набір. Використаємо URL створеного об’єкта (заголовок відповіді `Location`): Введемо data атрибут у поданому тілі: Задовільнимо вимогу типу вмісту: Подивимось, що показує список закупівель: Подивимось як працює точка входу `/tenders`: Оновимо закупівлю шляхом надання їй усіх інших важливих властивостей: Завантажимо документ угоди: Подивимось на список документів пов’язаних з угодою: Редагування закупівлі Спробуймо створити нову закупівлю: Можна отримати список запитань: Запит на скасування, який не пройшов активації (3-й крок), не матиме сили, тобто, для скасування закупівлі буде обов’язковим не тільки створити заявку, але і активувати її. Для того, щоб процедура відкритих торгів відбулась, необхідно хоча б два учасника, тобто хоча б дві пропозиції повинні бути зареєстровані до початку аукціону: Приготуйте запит на скасування. Формування запиту на скасування Замовник може відповісти на них: Замовник не може редагувати закупівлю, якщо залишилось менше 7 днів до завершення періоду подання пропозицій. API таких змін не прийме. Замовник може встановити забезпечення тендерної пропозиції: Замовник може завантажити PDF файл у створену закупівлю. Завантаження повинно відбуватись згідно правил :ref:`upload`. Завантаження пропозиції Кваліфікаційна комісія реєструє своє рішення: Реєстрація пропозиції Дивіться структуру запиту :ref:`cancellation` для більш детальної інформації. Дивіться на `Bid.participationUrl` у відповіді. Схожу, але іншу, URL-адресу можна отримати для інших учасників. Встановлення дати підписання угоди Встановлення терміну дії угоди Встановлення терміну дії угоди необов’язкове, але, якщо є необхідність, ви можете встановити відповідну дату початку `startDate` та кінця `endDate` терміну дії. Встановлення вартості угоди Успіх! Тепер ми бачимо, що новий об’єкт було створено. Код відповіді `201` та заголовок відповіді `Location` вказує місцерозташування створеного об’єкта. Тіло відповіді показує інформацію про створену закупівлю, її внутрішнє `id` (яке співпадає з сегментом `Location`), її офіційне `tenderID` та `dateModified` дату, що показує час, коли закупівля востаннє модифікувалась. Зверніть увагу, що закупівля створюється зі статусом `active.enquiries`. Той, хто створив закупівлю, може скасувати її у будь-який момент. Для цього виконайте наступні кроки: Статус закупівлі ``active.tendering`` дозволяє подання пропозицій. Ось чому потрібно продовжити період подання пропозицій на 7 днів. Особливість відкритих торгів в тому, що ``procurementMethodType`` було змінено з ``belowThreshold`` на ``aboveThresholdUA``.  Також тут неможливо встановити ``enquiryPeriod``, бо він буде призначений автоматично. Один елемент масиву описує завантажений документ. Ми можемо завантажити більше документів: Потім учасник повинен завантажити документ(и) пропозиції: При скасуванні, замовник має визначити один з двох типів ``reasonType``: торги відмінені - `cancelled`, або торги не відбулися - `unsuccessful`. За замовчуванням, значення ``reasonType`` рівне `cancelled`. Є можливість встановити дату підписання угоди. Для цього вставте відповідну дату в поле `dateSigned`. Туторіал Завантажити нову версію документа Завантажити вміст файлу Завантаження документації по угоді Завантаження документів Ми бачимо ту ж відповідь, що і після створення закупівлі. Ми бачимо внутрішнє `id` закупівлі (що може бути використано для побудови повної URL-адреси, якщо додати `http://api-sandbox.openprocurement.org/api/0/tenders/`) та її `dateModified` дату. Ми бачимо, що додаткові властивості об’єднані з існуючими даними закупівлі. Додатково оновлена властивість `dateModified`, щоб відображати останню дату модифікації. Якщо закупівля має статус ``active.tendering`` та дата завершення періоду подання пропозицій ``Tender.enqueryPeriod.endDate`` ще не прийшла , то зацікавлені учасники можуть задавати питання чи просити уточнень умов закупівлі: Ви можете виправити тип на `unsuccessful` (торги не відбулися). Ви можете завантажити документи угоди для процедури відкритих торгів. Ви повинні передати змінні `reason`, `status` у стані `pending`. Було повернуто код відповіді `200 OK`. Значення змінено успішно. Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було створено. Додатково можна зробити запит точки входу API колекції `документів`, щоб підтвердити дію: Код відповіді `201 Created` та заголовок `Location` підтверджують, що документ було додано. `id` генерується автоматично і повертається у додатковому заголовку відповіді `Location`: або окрему відповідь: 