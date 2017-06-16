# take the guardian articles and generate a csv

# import guardian articles
import os
import json
import csv
import re

from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=['http://controcurator.org:80/ess'])

es = Elasticsearch(
        ['http://controcurator.org/ess/'],
        port=80)

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

articles = ['https://www.theguardian.com/commentisfree/2017/apr/11/working-class-public-spaces-musee-d-orsay',
'https://www.theguardian.com/football/2017/apr/11/juventus-barcelona-champions-league-quarter-final-match-report',
'https://www.theguardian.com/world/2017/apr/11/us-defense-syria-chemical-weapons-attacks-assad-regime',
'https://www.theguardian.com/society/2017/apr/11/parents-fighting-to-keep-baby-charlie-gard-life-support-lose-high-court-battle',
'https://www.theguardian.com/football/2017/apr/11/borussia-dortmund-explosion-team-bus',
'https://www.theguardian.com/education/2017/apr/12/new-free-schools-despite-secondary-staff-cuts',
'https://www.theguardian.com/politics/2017/mar/21/martin-mcguinness-northern-ireland-former-deputy-first-minister-dies',
'https://www.theguardian.com/politics/2017/apr/12/foreign-states-may-have-interfered-in-brexit-vote-report-says',
'https://www.theguardian.com/us-news/2017/apr/11/homeland-security-searches-electronics-border',
'https://www.theguardian.com/environment/2017/mar/22/princess-anne-backs-gm-crops-livestock-unlike-prince-charles',
'https://www.theguardian.com/music/2017/apr/11/palestine-music-expo-pmx-musicians-shaking-up-the-occupied-territories',
'https://www.theguardian.com/world/2017/apr/11/g7-rejects-uk-call-for-sanctions-against-russia-and-syria',
'https://www.theguardian.com/commentisfree/2017/apr/11/frontline-brexit-culture-wars-ask-comedian-al-murray',
'https://www.theguardian.com/news/2017/apr/11/painting-a-new-picture-of-the-little-ice-age-weatherwatch',
'https://www.theguardian.com/us-news/2017/apr/11/detroit-michigan-500-dollar-house-rust-belt-america',
'https://www.theguardian.com/global-development/2017/apr/11/worrying-trend-as-aid-money-stays-in-wealthiest-countries',
'https://www.theguardian.com/society/2017/apr/11/recorded-childhood-cancers-rise-worldwide-world-health-organization',
'https://www.theguardian.com/commentisfree/2016/dec/08/modern-day-hermits-share-experiences',
'https://www.theguardian.com/football/2017/mar/22/ronnie-moran-liverpool-dies',
'https://www.theguardian.com/lifeandstyle/2017/apr/11/vision-thing-how-babies-colour-in-the-world',
'https://www.theguardian.com/world/2017/apr/11/nurses-grant-dying-man-final-wish-cigarette-glass-wine',
'https://www.theguardian.com/business/2017/apr/11/labour-declare-war-late-payers-marks-spencer-jeremy-corbyn',
'https://www.theguardian.com/science/2017/apr/12/scientists-unravel-mystery-of-the-loose-shoelace',
'https://www.theguardian.com/us-news/2017/apr/11/united-airlines-shares-plummet-passenger-removal-controversy',
'https://www.theguardian.com/business/2017/apr/11/judges-reject-us-bankers-claim-to-be-randy-work-genius-in-divorce-case',
'https://www.theguardian.com/business/2017/apr/12/tesco-profits-1bn-growth-supermarket',
'https://www.theguardian.com/money/2017/apr/11/probate-fees-plan-is-daft-as-well-as-devious',
'https://www.theguardian.com/commentisfree/2017/apr/11/donald-trump-russia-rex-tillersons-visit-syria',
'https://www.theguardian.com/environment/2017/apr/12/uk-butterflies-worst-hit-in-2016-with-70-of-species-in-decline-study-finds',
'https://www.theguardian.com/business/2017/apr/11/developing-countries-demands-for-better-life-must-be-met-says-world-bank-head',
'https://www.theguardian.com/politics/2017/apr/12/devon-and-cornwall-pcc-expenses-inquiry-prosecutors',
'https://www.theguardian.com/politics/shortcuts/2017/apr/11/deep-england-brexit-britain',
'https://www.theguardian.com/society/2017/apr/11/uk-supreme-court-denies-tobacco-firms-permission-for-plain-packaging-appeal',
'https://www.theguardian.com/society/2017/mar/21/dawn-butler-stood-up-for-deaf-people-but-we-need-more-than-gestures',
'https://www.theguardian.com/technology/2017/apr/11/gordon-ramsay-father-in-law-admits-hacking-company-computers',
'https://www.theguardian.com/tv-and-radio/2017/mar/20/richard-hammond-injured-in-grand-tour-crash-in-mozambique',
'https://www.theguardian.com/us-news/2017/apr/11/sean-spicer-hitler-chemical-weapons-holocaust-assad',
'https://www.theguardian.com/science/2017/mar/22/face-medieval-cambridge-man-emerges-700-years-after-death',
'https://www.theguardian.com/society/2017/mar/22/new-alzheimers-test-can-predict-age-when-disease-will-appear',
'https://www.theguardian.com/world/2017/apr/11/national-archives-mi5-file-new-zealand-diplomat-paddy-costello-kgb-spy',
'https://www.theguardian.com/australia-news/2017/mar/22/british-war-veteran-granted-permanent-residency-in-australia-ending-visa-drama',
'https://www.theguardian.com/books/2017/apr/11/x-men-illustrator-alleged-anti-christian-messages-marvel-ardian-syaf',
'https://www.theguardian.com/business/2017/apr/12/burger-king-ok-google-commercial',
'https://www.theguardian.com/business/2017/apr/12/edf-customers-price-rise-electricity-gas-energy',
'https://www.theguardian.com/business/2017/apr/12/ship-oil-rig-pioneer-spirit-shell-north-sea-decommissioning',
'https://www.theguardian.com/business/2017/mar/22/asian-shares-drop-investors-fear-trump-wont-deliver-promises',
'https://www.theguardian.com/football/2017/apr/11/tony-adams-vows-to-give-granada-players-a-kick-up-the-arse',
'https://www.theguardian.com/football/2017/mar/22/football-transfer-rumours-jermain-defoe-back-to-west-ham',
'https://www.theguardian.com/global-development/2017/apr/11/india-acts-to-help-acid-attack-victims',
'https://www.theguardian.com/money/2017/apr/11/student-loan-interest-rate-rise-uk-inflation-brexit',
'https://www.theguardian.com/uk-news/2017/mar/17/coroner-warns-of-dangers-after-man-electrocuted-in-bath-while-charging-phone',
'https://www.theguardian.com/business/2017/mar/22/london-taxi-company-coventry-electric-cabs-jobs-brexit',
'https://www.theguardian.com/commentisfree/2016/dec/14/experiences-accessing-mental-health-services-uk',
'https://www.theguardian.com/commentisfree/2017/apr/11/france-left-europe-jean-luc-melenchon-presidential-election',
'https://www.theguardian.com/commentisfree/2017/apr/11/sean-spicers-hitler-holocaust-speak-volumes',
'https://www.theguardian.com/commentisfree/2017/apr/11/united-airlines-flying-while-asian-fear',
'https://www.theguardian.com/environment/2017/mar/22/country-diary-long-mynd-shropshire-light-spout-waterfall',
'https://www.theguardian.com/football/2017/apr/11/borussia-dortmund-shock-team-bus-explosions',
'https://www.theguardian.com/football/2017/mar/17/stewart-downing-middlesbrough-karanka-row-agnew',
'https://www.theguardian.com/football/2017/mar/22/which-football-manager-has-been-sacked-by-one-club-the-most-times',
'https://www.theguardian.com/music/2017/mar/16/ed-sheeran-headline-sunday-night-glastonbury-2017',
'https://www.theguardian.com/sport/2017/apr/11/pennsylvania-woman-jail-threats-youth-football-league-officials',
'https://www.theguardian.com/sport/blog/2017/mar/22/talking-horses-best-wednesday-bets-for-warwick-and-newcastle',
'https://www.theguardian.com/technology/2017/mar/17/youtube-and-google-search-for-answers',
'https://www.theguardian.com/tv-and-radio/2017/mar/19/neighbours-tv-soap-could-disappear-from-british-screens',
'https://www.theguardian.com/uk-news/2017/apr/11/boris-johnson-full-support-failure-secure-sanctions-syria-russia',
'https://www.theguardian.com/world/2017/mar/22/brussels-unveil-terror-victims-memorial-one-year-after-attacks',
'https://www.theguardian.com/world/2017/mar/22/north-korea-missile-test-failure',
'https://www.theguardian.com/business/2017/mar/16/bank-of-england-uk-interest-rates-monetary-policy-committee',
'https://www.theguardian.com/business/2017/mar/21/inflation-uk-wages-lag-behind-prices-mark-carney',
'https://www.theguardian.com/business/2017/mar/22/nervous-markets-take-fright-at-prospect-of-trump-failing-to-deliver',
'https://www.theguardian.com/commentisfree/2016/dec/21/i-lost-my-mum-seven-weeks-ago-our-readers-on-coping-with-grief-at-christmas',
'https://www.theguardian.com/commentisfree/2017/jan/06/brexit-vote-have-you-applied-for-a-second-passport',
'https://www.theguardian.com/fashion/2017/mar/22/fiorucci-why-the-disco-friendly-label-is-perfect-for-2017',
'https://www.theguardian.com/film/2017/mar/17/from-the-corner-of-the-oval-obama-white-house-movie',
'https://www.theguardian.com/film/2017/mar/22/film-franchises-terminator-sequel-arnold-schwarzenegger-die-hard-alien',
'https://www.theguardian.com/law/2017/apr/12/judge-sacked-over-online-posts-calling-his-critics-donkeys',
'https://www.theguardian.com/lifeandstyle/2017/mar/17/monopoly-board-game-new-tokens-vote',
'https://www.theguardian.com/music/2017/mar/16/stormzy-condemns-nme-for-using-him-as-poster-boy-for-depression',
'https://www.theguardian.com/music/2017/mar/21/los-angeles-police-mistake-wyclef-jean-suspect-assault-case',
'https://www.theguardian.com/politics/2017/mar/22/uk-based-airlines-told-to-move-to-europe-after-brexit-or-lose-major-routes',
'https://www.theguardian.com/society/2017/apr/11/national-social-care-service-centralised-nhs',
'https://www.theguardian.com/sport/2017/mar/17/wales-france-six-nations-world-rankings',
'https://www.theguardian.com/tv-and-radio/2017/mar/22/n-word-taboo-tv-carmichael-show-atlanta-insecure-language',
'https://www.theguardian.com/uk-news/2017/mar/16/man-dies-explosion-former-petrol-station-highgate-north-london-swains-lane',
'https://www.theguardian.com/us-news/2017/mar/17/national-weather-service-forecasting-temperatures-storms',
'https://www.theguardian.com/us-news/2017/mar/22/fbi-muslim-employees-discrimination-religion-middle-east-travel',
'https://www.theguardian.com/us-news/2017/mar/22/zapier-pay-employees-move-silicon-valley-startup',
'https://www.theguardian.com/world/2017/mar/17/fleeing-from-dantes-hell-on-mount-etna',
'https://www.theguardian.com/world/2017/mar/22/gay-clergyman-jeffrey-johns-turned-down-welsh-bishop-twice-before-claims',
'https://www.theguardian.com/world/2017/mar/23/apple-paid-no-tax-in-new-zealand-for-at-least-a-decade-reports-say',
'https://www.theguardian.com/books/2017/mar/22/comics-chavez-redline-transformers-v-gi-joe',
'https://www.theguardian.com/business/2017/apr/11/uk-inflation-rate-stays-three-year-high',
'https://www.theguardian.com/commentisfree/2017/apr/12/charlie-gard-legal-aid',
'https://www.theguardian.com/commentisfree/2017/mar/22/rights-gig-economy-self-employed-worker',
'https://www.theguardian.com/media/2017/mar/14/face-off-mps-and-social-media-giants-online-hate-speech-facebook-twitter',
'https://www.theguardian.com/music/2017/apr/11/michael-buble-wife-says-son-noah-is-recovering-from-cancer',
'https://www.theguardian.com/society/2017/apr/11/bullying-and-violence-grip-out-of-control-guys-marsh-jail-dorset',
'https://www.theguardian.com/stage/2017/mar/22/trisha-brown-obituary',
'https://www.theguardian.com/travel/2017/mar/22/10-best-clubs-in-amsterdam-chosen-by-dj-experts',
'https://www.theguardian.com/us-news/2017/apr/11/us-universal-healthcare-single-payer-rallies',
'https://www.theguardian.com/us-news/2017/mar/22/us-border-agent-sexually-assaults-teenage-sisters-texas',
'https://www.theguardian.com/world/2017/apr/11/hundreds-of-refugees-missing-after-dunkirk-camp-fire',
'https://www.theguardian.com/world/2017/mar/22/unicef-condemns-sale-cambodian-breast-milk-us-mothers-firm-ambrosia-labs',
'https://www.theguardian.com/world/commentisfree/2017/mar/17/week-in-patriarchy-bbc-dad-jessica-valenti',
'https://www.theguardian.com/business/2017/mar/15/us-federal-reserve-raises-interest-rates-to-1',
'https://www.theguardian.com/business/2017/mar/21/london-cycle-courier-was-punished-for-refusing-work-after-eight-hours-in-cold',
'https://www.theguardian.com/football/2017/mar/17/tottenham-harry-kane-return-injury',
'https://www.theguardian.com/politics/2017/mar/15/browse-of-commons-explore-uk-parliament-with-first-virtual-tour',
'https://www.theguardian.com/politics/2017/mar/21/martin-mcguinness-sinn-fein-members-carry-coffin-home-in-derry',
'https://www.theguardian.com/sport/2017/mar/18/ireland-england-six-nations-dublin',
'https://www.theguardian.com/us-news/2017/mar/20/ivanka-trump-west-wing-office-security-clearance',
'https://www.theguardian.com/film/2017/mar/21/look-on-the-sweet-side-of-love-actually',
'https://www.theguardian.com/media/2017/mar/20/jamie-oliver-new-show-deal-channel-4-tv',
'https://www.theguardian.com/politics/2017/mar/16/theresa-may-vows-absolute-faith-in-hammond-after-u-turn',
'https://www.theguardian.com/politics/2017/mar/21/nicola-sturgeon-accused-of-hypocrisy-as-independence-debate-begins',
'https://www.theguardian.com/sport/2017/mar/17/jailed-transgender-fell-runner-thought-uk-athletics-was-trying-to-kill-her',
'https://www.theguardian.com/uk-news/2017/mar/16/former-marine-cleared-alexander-blackman-freed-immediately-ex-soldier-jail',
'https://www.theguardian.com/world/2017/mar/16/india-brexit-and-the-legacy-of-empire-in-africa',
'https://www.theguardian.com/world/2017/mar/18/a-good-looking-bird-the-bush-stone-curlew-that-loves-its-own-reflection',
'https://www.theguardian.com/world/2017/mar/21/electronics-ban-middle-east-flights-safety-hazards-airline-profit',
'https://www.theguardian.com/business/2017/mar/14/us-federal-reserve-interest-rates-janet-yellen-donald-trump',
'https://www.theguardian.com/business/2017/mar/16/rupert-murdoch-sky-bid-uk-ofcom',
'https://www.theguardian.com/business/2017/mar/20/us-forbids-devices-larger-cell-phones-flights-13-countries',
'https://www.theguardian.com/business/2017/mar/22/uk-ceos-national-living-wage-equality-trust-pay-gap',
'https://www.theguardian.com/football/2017/mar/17/arsene-wenger-granit-xhaka-referees',
'https://www.theguardian.com/lifeandstyle/2017/mar/17/chorizo-chicken-lemon-yoghurt-cavolo-nero-recipe-anna-hansen',
'https://www.theguardian.com/politics/2017/mar/17/george-osborne-london-evening-standard-editor-appointment-evgeny-lebedev',
'https://www.theguardian.com/uk-news/2017/mar/16/scotland-cannot-afford-to-ignore-its-deficit',
'https://www.theguardian.com/uk-news/2017/mar/17/prince-william-visits-paris-for-the-first-time-since-mother-dianas-death',
'https://www.theguardian.com/us-news/2017/mar/16/oc-actor-mischa-barton-speaks-out-sex-tapes-scandal',
'https://www.theguardian.com/world/2017/mar/15/uk-government-child-slavery-products-sold-britain-innovation-fund',
'https://www.theguardian.com/commentisfree/2017/mar/17/the-guardian-view-on-brexit-and-publishing-a-hardcore-problem',
'https://www.theguardian.com/politics/2017/mar/21/osborne-becomes-the-remainers-great-hope',
'https://www.theguardian.com/society/2017/mar/16/scotlands-exam-body-to-ensure-invigilators-get-living-wage',
'https://www.theguardian.com/society/2017/mar/18/rural-deprivation-and-ill-health-in-england-in-danger-of-being-overlooked',
'https://www.theguardian.com/sport/2017/mar/16/michael-oleary-team-not-ruling-out-return-mullins-yard-cheltenham-festival-horse-racing',
'https://www.theguardian.com/sport/2017/mar/17/ireland-v-england-lions-six-nations-rugby-union',
'https://www.theguardian.com/sport/2017/mar/18/this-is-your-night-conlans-dream-debut-wipes-out-nightmares-of-the-past',
'https://www.theguardian.com/sport/2017/mar/21/bha-dope-tests-horses-racecourse',
'https://www.theguardian.com/sport/2017/mar/21/donald-trump-colin-kaepernick-free-agent-anthem-protest',
'https://www.theguardian.com/uk-news/2017/mar/16/protect-survive-nuclear-war-republished-pamphlet',
'https://www.theguardian.com/uk-news/2017/mar/21/sisters-al-najjar-sue-cumberland-hotel-london-brutal-hammer-attack',
'https://www.theguardian.com/uk-news/2017/mar/22/what-support-does-your-employer-give-to-fathers',
'https://www.theguardian.com/artanddesign/2017/mar/21/winged-bull-and-giant-dollop-of-cream-to-adorn-trafalgar-squares-fourth-plinth',
'https://www.theguardian.com/books/2017/mar/17/the-bone-readers-jacob-ross-caribbean-thriller-jhalak-prize',
'https://www.theguardian.com/business/2017/mar/11/democrats-question-trump-conflict-of-interest-deutsche-bank-investigation-money-laundering',
'https://www.theguardian.com/business/2017/mar/17/barclays-bob-diamond-panmure-gordon',
'https://www.theguardian.com/commentisfree/2017/mar/15/brexit-was-an-english-vote-for-independence-you-cant-begrudge-the-scots-the-same',
'https://www.theguardian.com/environment/2017/mar/21/the-snow-buntings-drift-takes-them-much-further-than-somerset',
'https://www.theguardian.com/fashion/2017/mar/21/art-colour-victoria-beckham-van-gogh-fashion',
'https://www.theguardian.com/lifeandstyle/2017/mar/17/i-am-26-and-find-it-hard-to-meet-people-on-the-same-wavelength-as-me',
'https://www.theguardian.com/lifeandstyle/shortcuts/2017/mar/21/open-a-window-and-have-a-cold-shower-could-being-chilly-improve-your-health',
'https://www.theguardian.com/society/2017/mar/22/four-supersized-prisons-to-be-built-england-and-wales-elizabeth-truss-plan',
'https://www.theguardian.com/sport/2017/mar/17/ben-youngs-england-ireland-grand-slam-six-nations',
'https://www.theguardian.com/technology/2017/mar/17/google-ads-bike-helmets-adverts',
'https://www.theguardian.com/us-news/2017/mar/20/fbi-director-comey-confirms-investigation-trump-russia',
'https://www.theguardian.com/world/2017/mar/17/time-for-a-declaration-of-war-on-happiness']


fieldnames = ['id','url','title','paragraphCount','text','commentCount','comments','type','section','published']
filename = 'guardian'

# open file to write to
w = open(filename+'.csv', 'wb')
wr = csv.writer(w, delimiter=',',quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
wr.writerow(fieldnames)

# keep track of how many articles are used
count = 0
# keep list of seen articles

# go through each file
for file in articles:

    query = {
      "query": {
        "constant_score": {
          "filter": {
            "term": {
              "url": file
            }
          }
        }
      },
      "from": 0,
      "size": 1
    }

    response = es.search(index="controcurator", doc_type="article", body=query)
    if len(response['hits']['hits']) == 0:
        print "-- ARTICLE NOT FOUND --"
        continue
    print file

    article = response['hits']['hits'][0]['_source']

    if 'comments' not in article:
        print "-- NO COMMENTS --"
        continue

    socmed = [c['text'] for c in article['comments'] if 'type' in c and len(c['text']) < 300 and not c['text'].startswith('This comment was removed')][0:5]
    comments = [c['text'] for c in article['comments'] if 'type' not in c and len(c['text']) < 300 and not c['text'].startswith('This comment was removed')][0:5]
    print "SOCMED:",len(socmed)
    print "COMMENTS:",len(comments)

    if len(socmed) < 5:
        print 'TOO FEW SOCMED:',len(socmed)
        continue
        
    commentCount = len(socmed)

    paragraphs = article['document']['text'].split('</p>')
    text = '</p>'.join(paragraphs[:2]) + '</p>'


    # array for one row on the csv
    row = [
        response['hits']['hits'][0]['_id'],
        article['url'],
        article['document']['title'],
        0,
        text.encode('UTF-8'),
        commentCount,
        '||'.join(socmed).encode('UTF-8'),
        article['type'],
        0,
        article['published']
    ]


    #print 'SAVED:',title
    wr.writerow(row)
    count += 1

w.close()
print count