import os
import requests

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
        mutation = """
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
                                        emotionalProfile
                                        emotionalDynamics
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
        variables = {
            "input": {
                "spotifyTrackId": self.song_url  # Replace with the actual Spotify track ID
            }
        }

        # query data
        self.data = {
            "query": mutation,
            "operationName": "SpotifyTrackEnqueueMutation",
            "variables": variables
        }

    def get_data(self):
        # Send the POST request to the GraphQL endpoint
        response = requests.post(self.base_url, json=self.data, headers=self.headers)
        response = response.json()
        data = response['data']['spotifyTrackEnqueue']['enqueuedSpotifyTrack']['audioAnalysisV6']['result']
        mood = data['moodAdvanced']
        genre = data['genre']
        advancedGenre = data['advancedGenre']
        movement = data['movement']
        character = data['character']
        return mood, genre, advancedGenre, movement, character