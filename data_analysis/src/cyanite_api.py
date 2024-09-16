import os
import requests
import time

class CyaniteAPI(object):
    
    def __init__(self, song_url = "5sdQOyqq2IDhvmx2lHOpwd"):
        self.song_url = song_url

        # general
        self.current_dir = os.getcwd()
        self.base_url = "https://api.cyanite.ai/graphql"
        self.session = requests.Session()

        # authentication to process
        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiSW50ZWdyYXRpb25BY2Nlc3NUb2tlbiIsInZlcnNpb24iOiIxLjAiLCJpbnRlZ3JhdGlvbklkIjoxMTI4LCJ1c2VySWQiOjEyOTU2OCwiYWNjZXNzVG9rZW5TZWNyZXQiOiI3N2Q4ZWU5ZjE0NTkxYWU0N2NmYzg5Mjk4YmRiNTk0Nzc2MTQ1YzAzN2NkMzM1Mzk2YzE5ZDI4Y2RmZjY3M2RmIiwiaWF0IjoxNzIyMjAyMjUwfQ.-ZBpLthMR19Di9jFvb3fkCltX1BZOCLNZ9TfUTbZr2k"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'  # Replace with your actual access token if needed
        }

        # query mutation and variables
        self.musical_era_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        musicalEraTag
                                        classicalEpochTags
                                        classicalEpoch {
                                            middleAge
                                            renaissance
                                            baroque
                                            classical
                                            romantic
                                            contemporary
                                        }
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.vocal_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        voicePresenceProfile
                                        predominantVoiceGender
                                        voice {
                                            female
                                            male
                                            instrumental
                                        }
                                        voiceTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.genre_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        genre {
                                            ambient
                                            blues
                                            classical
                                            electronicDance
                                            folkCountry
                                            funkSoul
                                            jazz
                                            latin
                                            metal
                                            pop
                                            rapHipHop
                                            reggae
                                            rnb
                                            rock
                                            singerSongwriter
                                        }
                                        genreTags
                                        advancedGenre {
                                            afro
                                            ambient
                                            arab
                                            asian
                                            blues
                                            childrenJingle
                                            classical
                                            electronicDance
                                            folkCountry
                                            funkSoul
                                            indian
                                            jazz
                                            latin
                                            metal
                                            pop
                                            rapHipHop
                                            reggae
                                            rnb
                                            rock
                                            singerSongwriters
                                            sound
                                            soundtrack
                                            spokenWord
                                        }
                                        advancedGenreTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.sub_genre_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        subgenre {
                                            bluesRock
                                            folkRock
                                            hardRock
                                            indieAlternative
                                            psychedelicProgressiveRock
                                            punk
                                            rockAndRoll
                                            popSoftRock
                                            abstractIDMLeftfield
                                            breakbeatDnB
                                            deepHouse
                                            electro
                                            house
                                            minimal
                                            synthPop
                                            techHouse
                                            techno
                                            trance
                                            contemporaryRnB
                                            gangsta
                                            jazzyHipHop
                                            popRap
                                            trap
                                            blackMetal
                                            deathMetal
                                            doomMetal
                                            heavyMetal
                                            metalcore
                                            nuMetal
                                            disco
                                            funk
                                            gospel
                                            neoSoul
                                            soul
                                            bigBandSwing
                                            bebop
                                            contemporaryJazz
                                            easyListening
                                            fusion
                                            latinJazz
                                            smoothJazz
                                            country
                                            folk
                                        }
                                        subgenreTags
                                        advancedSubgenre {
                                            bluesRock
                                            folkRock
                                            hardRock
                                            indieAlternative
                                            psychedelicProgressiveRock
                                            punk
                                            rockAndRoll
                                            popSoftRock
                                            abstractIDMLeftfield
                                            breakbeatDnB
                                            deepHouse
                                            electro
                                            house
                                            minimal
                                            synthPop
                                            techHouse
                                            techno
                                            trance
                                            contemporaryRnB
                                            gangsta
                                            jazzyHipHop
                                            popRap
                                            trap
                                            blackMetal
                                            deathMetal
                                            doomMetal
                                            heavyMetal
                                            metalcore
                                            nuMetal
                                            disco
                                            funk
                                            gospel
                                            neoSoul
                                            soul
                                            bigBandSwing
                                            bebop
                                            contemporaryJazz
                                            easyListening
                                            fusion
                                            latinJazz
                                            smoothJazz
                                            country
                                            folk
                                        }
                                        advancedSubgenreTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.free_genre_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        freeGenreTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.transformer_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        transformerCaption
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.instrument_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        instrumentPresence {
                                            percussion
                                            synth
                                            piano
                                            acousticGuitar
                                            electricGuitar
                                            strings
                                            bass
                                            bassGuitar
                                            brassWoodwinds
                                        }
                                        advancedInstrumentPresence {
                                            percussion
                                            synth
                                            piano
                                            acousticGuitar
                                            electricGuitar
                                            strings
                                            bass
                                            bassGuitar
                                            brass
                                            woodwinds
                                        }
                                        advancedInstrumentPresenceExtended {
                                            acousticGuitar
                                            bass
                                            bassGuitar
                                            electricGuitar
                                            percussion
                                            piano
                                            synth
                                            strings
                                            brass
                                            woodwinds
                                            tuba
                                            frenchHorn
                                            oboe
                                            mandolin
                                            cello
                                            marimba
                                            vibraphone
                                            electricPiano
                                            electricOrgan
                                            harp
                                            ukulele
                                            harpsichord
                                            churchOrgan
                                            doubleBass
                                            glockenspiel
                                            electronicDrums
                                            drumKit
                                            accordion
                                            violin
                                            flute
                                            sax
                                            trumpet
                                            celeste
                                            pizzicato
                                            banjo
                                            clarinet
                                            bells
                                            steelDrums
                                            bongoConga
                                            africanPercussion
                                            tabla
                                            sitar
                                            taiko
                                            asianFlute
                                            asianStrings
                                            luteOud
                                        }
                                        instrumentTags
                                        advancedInstrumentTags
                                        advancedInstrumentTagsExtended
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.emotion_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        emotionalProfile
                                        emotionalDynamics
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.mood_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        mood {
                                            aggressive
                                            calm
                                            chilled
                                            dark
                                            energetic
                                            epic
                                            happy
                                            romantic
                                            sad
                                            scary
                                            sexy
                                            ethereal
                                            uplifting
                                        }
                                        moodTags
                                        moodMaxTimes {
                                            mood
                                            start
                                            end
                                        }
                                        moodAdvanced {
                                            anxious
                                            barren
                                            cold
                                            creepy
                                            dark
                                            disturbing
                                            eerie
                                            evil
                                            fearful
                                            mysterious
                                            nervous
                                            restless
                                            spooky
                                            strange
                                            supernatural
                                            suspenseful
                                            tense
                                            weird
                                            aggressive
                                            agitated
                                            angry
                                            dangerous
                                            fiery
                                            intense
                                            passionate
                                            ponderous
                                            violent
                                            comedic
                                            eccentric
                                            funny
                                            mischievous
                                            quirky
                                            whimsical
                                            boisterous
                                            boingy
                                            bright
                                            celebratory
                                            cheerful
                                            excited
                                            feelGood
                                            fun
                                            happy
                                            joyous
                                            lighthearted
                                            perky
                                            playful
                                            rollicking
                                            upbeat
                                            calm
                                            contented
                                            dreamy
                                            introspective
                                            laidBack
                                            leisurely
                                            lyrical
                                            peaceful
                                            quiet
                                            relaxed
                                            serene
                                            soothing
                                            spiritual
                                            tranquil
                                            bittersweet
                                            blue
                                            depressing
                                            gloomy
                                            heavy
                                            lonely
                                            melancholic
                                            mournful
                                            poignant
                                            sad
                                            frightening
                                            horror
                                            menacing
                                            nightmarish
                                            ominous
                                            panicStricken
                                            scary
                                            concerned
                                            determined
                                            dignified
                                            emotional
                                            noble
                                            serious
                                            solemn
                                            thoughtful
                                            cool
                                            seductive
                                            sexy
                                            adventurous
                                            confident
                                            courageous
                                            resolute
                                            energetic
                                            epic
                                            exciting
                                            exhilarating
                                            heroic
                                            majestic
                                            powerful
                                            prestigious
                                            relentless
                                            strong
                                            triumphant
                                            victorious
                                            delicate
                                            graceful
                                            hopeful
                                            innocent
                                            intimate
                                            kind
                                            light
                                            loving
                                            nostalgic
                                            reflective
                                            romantic
                                            sentimental
                                            soft
                                            sweet
                                            tender
                                            warm
                                            anthemic
                                            aweInspiring
                                            euphoric
                                            inspirational
                                            motivational
                                            optimistic
                                            positive
                                            proud
                                            soaring
                                            uplifting
                                        }
                                        moodAdvancedTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.character_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        character {
                                            bold
                                            cool
                                            epic
                                            ethereal
                                            heroic
                                            luxurious
                                            magical
                                            mysterious
                                            playful
                                            powerful
                                            retro
                                            sophisticated
                                            sparkling
                                            sparse
                                            unpolished
                                            warm
                                        }
                                        characterTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.movement_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        movement {
                                            bouncy
                                            driving
                                            flowing
                                            groovy
                                            nonrhythmic
                                            pulsing
                                            robotic
                                            running
                                            steady
                                            stomping
                                        }
                                        movementTags
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.misc_mutation = """
            mutation SpotifyTrackEnqueueMutation($input: SpotifyTrackEnqueueInput!) {
                spotifyTrackEnqueue(input: $input) {
                    __typename
                    ... on SpotifyTrackEnqueueSuccess {
                        enqueuedSpotifyTrack {
                            id
                            audioAnalysisV6 {
                                __typename
                                ... on AudioAnalysisV6Finished {
                                    result {
                                        energyLevel
                                        energyDynamics
                                        bpmPrediction {
                                        value
                                        confidence
                                        }
                                        bpmRangeAdjusted
                                        keyPrediction {
                                        value
                                        confidence
                                        }
                                        timeSignature
                                    }
                                }
                            }
                        }
                    }
                    ... on Error {
                        message
                    }
                }
            }
            """
        
        self.variables = {
            "input": {
                "spotifyTrackId": self.song_url  # Replace with the actual Spotify track ID
            }
        }

    def get_data(self, data):
        """
    Send the POST request to the GraphQL endpoint with error handling
    """
        time.sleep(0.5)
        try:
            response = self.session.post(self.base_url, json=data, headers=self.headers)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            response_json = response.json()
            if 'data' in response_json and 'spotifyTrackEnqueue' in response_json['data']:
                data = response_json['data']['spotifyTrackEnqueue']
                if 'enqueuedSpotifyTrack' in data:
                    track_data = data['enqueuedSpotifyTrack']['audioAnalysisV6']['result']
                    return track_data
                elif 'Error' in data:
                    print(f"Error: {data['Error']['message']}")
            else:
                print("Unexpected response format:", response_json)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        return {}
        
    def get_all_data(self):
        """
            Retrieve data on song
        """
        # musical era retrieval
        data = {
            "query": self.musical_era_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        musical_era = self.get_data(data)['musicalEraTag']
        # voice retrieval
        data = {
            "query": self.vocal_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        voice_presence = self.get_data(data)['voicePresenceProfile']
        predominant_voice_gender = self.get_data(data)['predominantVoiceGender']
        # genre retrieval
        data = {
            "query": self.genre_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        genreTags = self.get_data(data)['genreTags']
        genre = self.get_data(data)['genre']
        # sub genre retrieval
        data = {
            "query": self.sub_genre_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        subgenre = self.get_data(data)['subgenre']
        subgenreTags = self.get_data(data)['subgenreTags']
        # free genre retrieval
        data = {
            "query": self.free_genre_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        freegenre = self.get_data(data)['freeGenreTags']
        # description retrieval
        data = {
            "query": self.transformer_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        description = self.get_data(data)['transformerCaption']
        # instrument retrieval
        data = {
            "query": self.instrument_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        instrumentTags = self.get_data(data)['instrumentTags']
        instrument = self.get_data(data)['advancedInstrumentPresence']
        # emotion retrieval
        data = {
            "query": self.emotion_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        emotionProfile = self.get_data(data)['emotionalProfile']
        # mood retrieval
        data = {
            "query": self.mood_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        moodTags = self.get_data(data)['moodAdvancedTags']
        mood = self.get_data(data)['moodAdvanced']
        simple_moodTags = self.get_data(data)['moodTags']
        simple_mood = self.get_data(data)['mood']
        # character retrieval
        data = {
            "query": self.character_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        character = self.get_data(data)['character']
        characterTags = self.get_data(data)['characterTags']
        # movement retrieval
        data = {
            "query": self.movement_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        movement = self.get_data(data)['movement']
        movementTags = self.get_data(data)['movementTags']
        # misc retrieval
        data = {
            "query": self.misc_mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": self.variables
        }
        energy = self.get_data(data)['energyLevel']
        bpm = self.get_data(data)['bpmPrediction']
        key = self.get_data(data)['keyPrediction']
        meter = self.get_data(data)['timeSignature']

        result = {'Musical_Era': musical_era, 'Voice_Presence': voice_presence, 'Predominant_Voice_Gender': predominant_voice_gender, 
                  'Genre_Tags': genreTags, 'Genre': genre, 'Sub_Genre': subgenre, 'Sub_Genre_Tags': subgenreTags, 'Free Genre': freegenre, 
                  'Description': description, 'Instrument': instrument, 'Instrument_Tags': instrumentTags, 'Emotional_Profile': emotionProfile,
                  'Mood_Tags': moodTags, 'Mood': mood, 'Simple_Mood': simple_mood, 'Simple_Mood_Tags': simple_moodTags, 'Character': character,
                  'Character_Tags': characterTags, 'Movement': movement, 'Movement_Tags': movementTags, 'Energy': energy, 'BPM': bpm,
                  'Key': key, 'Meter': meter}
        return result
cyanite = CyaniteAPI()
cyanite.get_all_data()