import json
import requests
import time
try:
    from IMDBTraktSyncer import errorHandling as EH
except ImportError:
    import errorHandling as EH

def getTraktData():
    # Process Trakt Ratings and Comments
    print('Processing Trakt Ratings and Comments')

    response = EH.make_trakt_request('https://api.trakt.tv/users/me')
    json_data = json.loads(response.text)
    username = json_data['username']

    # Get Trakt Ratings
    response = EH.make_trakt_request(f'https://api.trakt.tv/users/{username}/ratings')
    json_data = json.loads(response.text)

    movie_ratings = []
    show_ratings = []
    episode_ratings = []

    for item in json_data:
        if item['type'] == 'movie':
            movie = item.get('movie')
            movie_id = movie.get('ids', {}).get('imdb')
            movie_ratings.append({'Title': movie.get('title'), 'Year': movie.get('year'), 'Rating': item.get('rating'), 'ID': movie_id, 'Type': 'movie'})
        elif item['type'] == 'show':
            show = item.get('show')
            show_id = show.get('ids', {}).get('imdb')
            show_ratings.append({'Title': show.get('title'), 'Year': show.get('year'), 'Rating': item.get('rating'), 'ID': show_id, 'Type': 'show'})
        elif item['type'] == 'episode':
            show = item.get('show')
            show_title = show.get('title')
            episode = item.get('episode')
            episode_id = episode.get('ids', {}).get('imdb')
            episode_title = f'{show_title}: {episode.get("title")}'
            episode_ratings.append({'Title': episode_title, 'Year': episode.get('year'), 'Rating': item.get('rating'), 'ID': episode_id, 'Type': 'episode'})

    trakt_ratings = movie_ratings + show_ratings + episode_ratings

    # Get Trakt Comments
    response = EH.make_trakt_request(f'https://api.trakt.tv/users/{username}/comments')
    json_data = json.loads(response.text)
    total_pages = response.headers.get('X-Pagination-Page-Count')
    trakt_comments = []

    for page in range(1, int(total_pages) + 1):
        response = EH.make_trakt_request(f'https://api.trakt.tv/users/{username}/comments', params={'page': page})
        json_data = json.loads(response.text)

        for comment in json_data:
            comment_type = comment['type']
            spoiler = comment.get('spoiler', False)

            if comment_type == 'movie':
                movie = comment.get('movie')
                show_movie_or_episode_title = movie.get('title')
                show_movie_or_episode_year = movie.get('year')
                show_movie_or_episode_imdb_id = movie.get('ids', {}).get('imdb')
            elif comment_type == 'episode':
                show = comment.get('show')
                episode = comment.get('episode')
                show_movie_or_episode_title = f"{show.get('title')}: {episode.get('title')}"
                show_movie_or_episode_year = show.get('year')
                show_movie_or_episode_imdb_id = episode.get('ids', {}).get('imdb')
            elif comment_type == 'show':
                show = comment.get('show')
                show_movie_or_episode_title = show.get('title')
                show_movie_or_episode_year = show.get('year')
                show_movie_or_episode_imdb_id = show.get('ids', {}).get('imdb')
            elif comment_type == 'season':
                show = comment.get('show')
                season = comment.get('season')
                show_movie_or_episode_title = f"{show.get('title')}: Season {season.get('number')}"
                show_movie_or_episode_year = None
                show_movie_or_episode_imdb_id = None
            else:
                show_movie_or_episode_title = None
                show_movie_or_episode_year = None
                show_movie_or_episode_imdb_id = None

            comment_info = comment['comment']
            trakt_comment_id = comment_info.get('id')
            trakt_comment = comment_info.get('comment')

            trakt_comments.append({
                'Title': show_movie_or_episode_title,
                'Year': show_movie_or_episode_year,
                'ID': show_movie_or_episode_imdb_id,
                'TraktCommentID': trakt_comment_id,
                'Comment': trakt_comment,
                'Spoiler': spoiler,
                'Type': comment_type
            })

    print('Processing Trakt Ratings and Comments Complete')

    return trakt_ratings, trakt_comments