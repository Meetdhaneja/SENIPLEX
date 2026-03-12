"""Seed database with initial data"""
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.user import User
from app.models.genre import Genre
from app.models.country import Country
from app.models.movie import Movie
from app.core.security import get_password_hash
from app.core.config import settings
from loguru import logger


def seed_admin_user(db: Session):
    """Create admin user"""
    admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    if not admin:
        admin = User(
            email=settings.ADMIN_EMAIL,
            username=settings.ADMIN_USERNAME,
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_admin=True,
            is_active=True
        )
        db.add(admin)
        db.commit()
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists")


def seed_genres(db: Session):
    """Create default genres"""
    genres = [
        "Action", "Comedy", "Drama", "Horror", "Thriller",
        "Romance", "Sci-Fi", "Fantasy", "Documentary", "Animation",
        "Crime", "Mystery", "Adventure", "Family", "War"
    ]
    
    for genre_name in genres:
        genre = db.query(Genre).filter(Genre.name == genre_name).first()
        if not genre:
            genre = Genre(name=genre_name)
            db.add(genre)
    
    db.commit()
    logger.info(f"Seeded {len(genres)} genres")


def seed_countries(db: Session):
    """Create default countries"""
    countries = [
        "United States", "United Kingdom", "India", "Canada", "Australia",
        "France", "Germany", "Japan", "South Korea", "Spain",
        "Italy", "Brazil", "Mexico", "China", "Russia"
    ]
    
    for country_name in countries:
        country = db.query(Country).filter(Country.name == country_name).first()
        if not country:
            country = Country(name=country_name)
            db.add(country)
    
    db.commit()
    logger.info(f"Seeded {len(countries)} countries")


def seed_movies(db: Session):
    """Seed sample movies"""
    count = db.query(Movie).count()
    if count > 0:
        logger.info(f"Movies already seeded ({count} found), skipping")
        return

    sample_movies = [
        {
            "title": "Inception",
            "description": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
            "release_year": 2010,
            "duration_minutes": 148,
            "rating": 9.0,
            "imdb_rating": 8.8,
            "content_type": "Movie",
            "director": "Christopher Nolan",
            "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Elliot Page, Tom Hardy",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
            "is_featured": True,
        },
        {
            "title": "The Dark Knight",
            "description": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability.",
            "release_year": 2008,
            "duration_minutes": 152,
            "rating": 9.2,
            "imdb_rating": 9.0,
            "content_type": "Movie",
            "director": "Christopher Nolan",
            "cast": "Christian Bale, Heath Ledger, Aaron Eckhart, Michael Caine",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
            "is_featured": True,
        },
        {
            "title": "Interstellar",
            "description": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
            "release_year": 2014,
            "duration_minutes": 169,
            "rating": 8.9,
            "imdb_rating": 8.6,
            "content_type": "Movie",
            "director": "Christopher Nolan",
            "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
            "is_featured": True,
        },
        {
            "title": "The Shawshank Redemption",
            "description": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "release_year": 1994,
            "duration_minutes": 142,
            "rating": 9.5,
            "imdb_rating": 9.3,
            "content_type": "Movie",
            "director": "Frank Darabont",
            "cast": "Tim Robbins, Morgan Freeman, Bob Gunton",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=6hB3S9bIaco",
            "is_featured": False,
        },
        {
            "title": "Avengers: Endgame",
            "description": "After the devastating events of Infinity War, the Avengers assemble once more in order to reverse Thanos' actions and restore balance to the universe.",
            "release_year": 2019,
            "duration_minutes": 181,
            "rating": 8.8,
            "imdb_rating": 8.4,
            "content_type": "Movie",
            "director": "Anthony Russo, Joe Russo",
            "cast": "Robert Downey Jr., Chris Evans, Mark Ruffalo, Chris Hemsworth",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/or06FN3Dka5tukK1e9sl16pB3iy.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=TcMBFSGVi1c",
            "is_featured": True,
        },
        {
            "title": "Parasite",
            "description": "Greed and class discrimination threaten the newly formed symbiotic relationship between the wealthy Park family and the destitute Kim clan.",
            "release_year": 2019,
            "duration_minutes": 132,
            "rating": 9.1,
            "imdb_rating": 8.5,
            "content_type": "Movie",
            "director": "Bong Joon-ho",
            "cast": "Song Kang-ho, Lee Sun-kyun, Cho Yeo-jeong",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=isOGD_7hNIY",
            "is_featured": True,
        },
        {
            "title": "The Matrix",
            "description": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
            "release_year": 1999,
            "duration_minutes": 136,
            "rating": 8.9,
            "imdb_rating": 8.7,
            "content_type": "Movie",
            "director": "Lana Wachowski, Lilly Wachowski",
            "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
            "is_featured": False,
        },
        {
            "title": "Dune",
            "description": "Feature adaptation of Frank Herbert's science fiction novel about the son of a noble family entrusted with the protection of the most valuable asset in the galaxy.",
            "release_year": 2021,
            "duration_minutes": 155,
            "rating": 8.3,
            "imdb_rating": 8.0,
            "content_type": "Movie",
            "director": "Denis Villeneuve",
            "cast": "Timothée Chalamet, Rebecca Ferguson, Oscar Isaac, Zendaya",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/d5NXSklpcvwho0TKFJo3Rr3lOiB.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=8g18jFHCLXk",
            "is_featured": True,
        },
        {
            "title": "Breaking Bad",
            "description": "A high school chemistry teacher diagnosed with inoperable lung cancer turns to manufacturing and selling methamphetamine in order to secure his family's future.",
            "release_year": 2008,
            "duration_minutes": 47,
            "rating": 9.5,
            "imdb_rating": 9.5,
            "content_type": "TV Show",
            "director": "Vince Gilligan",
            "cast": "Bryan Cranston, Aaron Paul, Anna Gunn",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/ggFHVNu6YYI5L9pCfOacjizRGt.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=HhesaQXLuRY",
            "is_featured": True,
        },
        {
            "title": "Stranger Things",
            "description": "When a young boy vanishes, a small town uncovers a mystery involving secret experiments, terrifying supernatural forces and one strange little girl.",
            "release_year": 2016,
            "duration_minutes": 51,
            "rating": 8.8,
            "imdb_rating": 8.7,
            "content_type": "TV Show",
            "director": "The Duffer Brothers",
            "cast": "Millie Bobby Brown, Finn Wolfhard, Winona Ryder",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/49WJfeN0moxb9IPfGn8AIqMGskD.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=b9EkMc79ZSU",
            "is_featured": True,
        },
        {
            "title": "Spider-Man: No Way Home",
            "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear.",
            "release_year": 2021,
            "duration_minutes": 148,
            "rating": 8.5,
            "imdb_rating": 8.3,
            "content_type": "Movie",
            "director": "Jon Watts",
            "cast": "Tom Holland, Zendaya, Benedict Cumberbatch",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/uJYYizSuA9Y3DCs0qS4qWvHfZg4.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=JfVOs4VSpmA",
            "is_featured": False,
        },
        {
            "title": "The Godfather",
            "description": "An organized crime dynasty's aging patriarch transfers control of his clandestine empire to his reluctant son.",
            "release_year": 1972,
            "duration_minutes": 175,
            "rating": 9.7,
            "imdb_rating": 9.2,
            "content_type": "Movie",
            "director": "Francis Ford Coppola",
            "cast": "Marlon Brando, Al Pacino, James Caan",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/3bhkrj58Vtu7enYsLMdL73rXDd9.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=sY1S34973zA",
            "is_featured": False,
        },
        {
            "title": "Oppenheimer",
            "description": "The story of American scientist J. Robert Oppenheimer and his role in the development of the atomic bomb during World War II.",
            "release_year": 2023,
            "duration_minutes": 180,
            "rating": 9.0,
            "imdb_rating": 8.9,
            "content_type": "Movie",
            "director": "Christopher Nolan",
            "cast": "Cillian Murphy, Emily Blunt, Matt Damon, Robert Downey Jr.",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=uYPbbksJxIg",
            "is_featured": True,
        },
        {
            "title": "Squid Game",
            "description": "Hundreds of cash-strapped players accept a strange invitation to compete in children's games. Inside, a tempting prize awaits — with deadly high stakes.",
            "release_year": 2021,
            "duration_minutes": 54,
            "rating": 8.5,
            "imdb_rating": 8.0,
            "content_type": "TV Show",
            "director": "Hwang Dong-hyuk",
            "cast": "Lee Jung-jae, Park Hae-soo, Wi Ha-jun",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/dDlEmu3EZ0Pgg93K2SVNLCjCSvE.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=oqxAJKy0ii4",
            "is_featured": True,
        },
        {
            "title": "Fight Club",
            "description": "An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.",
            "release_year": 1999,
            "duration_minutes": 139,
            "rating": 9.0,
            "imdb_rating": 8.8,
            "content_type": "Movie",
            "director": "David Fincher",
            "cast": "Brad Pitt, Edward Norton, Helena Bonham Carter",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=SUXWAEX2jlg",
            "is_featured": False,
        },
        {
            "title": "Pulp Fiction",
            "description": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
            "release_year": 1994,
            "duration_minutes": 154,
            "rating": 9.3,
            "imdb_rating": 8.9,
            "content_type": "Movie",
            "director": "Quentin Tarantino",
            "cast": "John Travolta, Uma Thurman, Samuel L. Jackson",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=s7EdQ4FqbhY",
            "is_featured": False,
        },
        {
            "title": "Joker",
            "description": "A gritty character study of Arthur Fleck, a man disregarded by society who is pushed too far and becomes the infamous Joker.",
            "release_year": 2019,
            "duration_minutes": 122,
            "rating": 8.7,
            "imdb_rating": 8.4,
            "content_type": "Movie",
            "director": "Todd Phillips",
            "cast": "Joaquin Phoenix, Robert De Niro, Zazie Beetz",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/udDclJoHjfjb8Ekgsd4FDteOkCU.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=zAGVQLHvwOY",
            "is_featured": False,
        },
        {
            "title": "3 Idiots",
            "description": "Two friends are reminiscing about their college days and set out to find a lost buddy, while reliving their adventure through engineering school.",
            "release_year": 2009,
            "duration_minutes": 170,
            "rating": 9.2,
            "imdb_rating": 8.4,
            "content_type": "Movie",
            "director": "Rajkumar Hirani",
            "cast": "Aamir Khan, Madhavan, Sharman Joshi, Kareena Kapoor",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/66A9MqXQ4G9qjWsDr1W5gBELDJq.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=K0eDlFX9GMc",
            "is_featured": False,
        },
        {
            "title": "Spirited Away",
            "description": "During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and her parents are turned into pigs.",
            "release_year": 2001,
            "duration_minutes": 125,
            "rating": 9.3,
            "imdb_rating": 8.6,
            "content_type": "Movie",
            "director": "Hayao Miyazaki",
            "cast": "Daveigh Chase, Suzanne Pleshette, Miyu Irino",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=ByXuk9QqQkk",
            "is_featured": False,
        },
        {
            "title": "Barbie",
            "description": "Barbie and Ken are having the time of their lives in the colorful and seemingly perfect world of Barbie Land. However, when they get a chance to go to the real world, Barbie faces the challenges of fitting in.",
            "release_year": 2023,
            "duration_minutes": 114,
            "rating": 7.8,
            "imdb_rating": 6.9,
            "content_type": "Movie",
            "director": "Greta Gerwig",
            "cast": "Margot Robbie, Ryan Gosling, America Ferrera",
            "thumbnail_url": "https://image.tmdb.org/t/p/w500/iuFNMS8vlbLdbB0gkvOFvFMWR6O.jpg",
            "trailer_url": "https://www.youtube.com/watch?v=pBk4NYhWNMM",
            "is_featured": False,
        },
    ]

    for movie_data in sample_movies:
        movie = Movie(**movie_data)
        db.add(movie)

    db.commit()
    logger.info(f"Seeded {len(sample_movies)} movies successfully")


def seed_database():
    """Seed all initial data"""
    db = SessionLocal()
    try:
        seed_admin_user(db)
        seed_genres(db)
        seed_countries(db)
        seed_movies(db)
        logger.info("Database seeding completed")
    except Exception as e:
        logger.error(f"Error seeding database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
