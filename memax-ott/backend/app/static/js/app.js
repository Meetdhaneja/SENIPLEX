document.addEventListener('DOMContentLoaded', async () => {
    console.log("MEMAX OTT Frontend Loaded");

    // DOM Elements
    const trendingRow = document.getElementById('trending-row');
    const newReleasesRow = document.getElementById('new-releases-row');
    const searchSection = document.getElementById('search-section');
    const searchResultsRow = document.getElementById('search-results-row');
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');

    // Auth Elements
    const authBtn = document.getElementById('auth-btn');
    const userMenu = document.getElementById('user-menu');
    const userGreeting = document.getElementById('user-greeting');
    const logoutBtn = document.getElementById('logout-btn');

    // Protected Sections
    const recommendedSection = document.getElementById('recommended-section');
    const recommendedRow = document.getElementById('recommended-row');
    const myListSection = document.getElementById('mylist-section');
    const myListRow = document.getElementById('my-list-row');

    // Token Management
    const token = localStorage.getItem('token');
    let user = null;

    // --- Authentication State ---
    if (token) {
        console.log("User logged in");
        authBtn.style.display = 'none';
        userMenu.style.display = 'flex';
        // Decode token simple check or fetch 'me' (skipping decode lib for now, assuming valid)
        userGreeting.textContent = "Welcome back!";

        // Show protected sections
        recommendedSection.style.display = 'block';
        mylistSection.style.display = 'block';

        // Fetch Protected Data
        loadProtectedData();
    } else {
        console.log("User guest mode");
    }

    logoutBtn.addEventListener('click', () => {
        localStorage.removeItem('token');
        window.location.reload();
    });

    // --- Search Functionality ---
    async function performSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        searchSection.style.display = 'block';
        searchResultsRow.innerHTML = '<div class="loading-skeleton"></div>';

        try {
            const results = await fetchMovies(`search?q=${encodeURIComponent(query)}`);
            searchResultsRow.innerHTML = '';

            if (results.length === 0) {
                searchResultsRow.innerHTML = '<p style="padding: 1rem; color: #aaa;">No results found.</p>';
                return;
            }

            results.forEach(movie => {
                searchResultsRow.appendChild(createMovieCard(movie));
            });

            // Scroll to search results
            searchSection.scrollIntoView({ behavior: 'smooth' });
        } catch (err) {
            console.error(err);
        }
    }

    if (searchBtn) searchBtn.addEventListener('click', performSearch);
    if (searchInput) searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // --- Data Fetching ---
    async function fetchMovies(endpoint, method = 'GET', body = null) {
        try {
            const headers = { 'Content-Type': 'application/json' };
            if (token) headers['Authorization'] = `Bearer ${token}`;

            const options = {
                method,
                headers,
                body: body ? JSON.stringify(body) : null
            };

            const response = await fetch(`/api/movies/${endpoint}`, options);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();

            if (Array.isArray(data)) return data;
            if (data.movies && Array.isArray(data.movies)) return data.movies;
            return [];
        } catch (error) {
            console.error(`Error fetching ${endpoint}:`, error);
            return [];
        }
    }

    async function fetchProtected(endpoint) {
        try {
            const response = await fetch(`/api/${endpoint}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!response.ok) return [];
            return await response.json();
        } catch (e) {
            console.error(e);
            return [];
        }
    }

    // --- Render Functions ---
    function createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        const poster = movie.poster_url || movie.poster_path || `https://via.placeholder.com/200x300?text=${encodeURIComponent(movie.title)}`;
        const matchScore = movie.match_score || (Math.floor(Math.random() * 20) + 80); // Simulate match score if missing

        card.innerHTML = `
            <img src="${poster}" alt="${movie.title}" loading="lazy">
            <div class="card-overlay">
                <div class="card-title">${movie.title}</div>
                <div class="card-meta">
                    <span style="color: #4ade80;">${matchScore}% Match</span>
                    <span>${movie.release_date ? movie.release_date.substring(0, 4) : (movie.year || '2023')}</span>
                </div>
                <div class="hero-buttons" style="margin-top: 0.5rem; gap: 0.5rem;">
                   <button class="btn btn-primary" onclick="window.openVideoModal('${movie.title.replace(/'/g, "\\'")}')" style="padding: 0.3rem 0.8rem; font-size: 0.7rem;">
                        <i class="fas fa-play"></i>
                   </button>
                   <button class="btn-icon" onclick="toggleLike(${movie.id}, this)">
                        <i class="fas fa-heart"></i>
                   </button>
                   <button class="btn-icon" onclick="addToMyList(${movie.id}, this)">
                        <i class="fas fa-plus"></i>
                   </button>
                </div>
            </div>
        `;
        return card;
    }

    async function renderSection(rowElement, endpoint, isProtected = false) {
        let movies = [];
        if (isProtected) {
            if (endpoint === 'recommendations') {
                const res = await fetchProtected('recommendations/personalized', 'POST', { limit: 10 });
                movies = res.recommendations ? res.recommendations.map(r => r.movie) : [];
            } else if (endpoint === 'likes') {
                movies = await fetchProtected('likes');
            }
        } else {
            movies = await fetchMovies(endpoint);
        }

        rowElement.innerHTML = '';
        if (!movies || movies.length === 0) {
            rowElement.innerHTML = '<p style="color: grey; padding: 1rem;">No content available.</p>';
            return;
        }

        movies.forEach(movie => {
            rowElement.appendChild(createMovieCard(movie));
        });
    }

    async function loadProtectedData() {
        // Recommendations
        const recRes = await fetch('/api/recommendations/personalized', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ limit: 10, exclude_watched: true })
        });

        if (recRes.ok) {
            const data = await recRes.json();
            const recMovies = data.recommendations ? data.recommendations.map(r => r.movie) : [];
            recommendedRow.innerHTML = '';
            recMovies.forEach(m => recommendedRow.appendChild(createMovieCard(m)));
        }

        // My List (Likes for now)
        const likesRes = await fetch('/api/likes', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (likesRes.ok) {
            const likedMovies = await likesRes.json();
            myListRow.innerHTML = '';
            likedMovies.forEach(m => myListRow.appendChild(createMovieCard(m)));
        }
    }

    // --- Interactions ---
    window.toggleLike = async (movieId, btn) => {
        if (!token) return alert("Please sign in to like movies");

        // Optimistic UI update
        const icon = btn.querySelector('i');
        const isLiked = btn.classList.contains('active');

        if (isLiked) {
            btn.classList.remove('active');
            // Call API to unlike
            try {
                await fetch(`/api/likes/${movieId}`, {
                    method: 'DELETE',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            } catch (e) { console.error(e); }
        } else {
            btn.classList.add('active');
            // Call API to like
            try {
                await fetch(`/api/likes?movie_id=${movieId}`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${token}` }
                });
            } catch (e) { console.error(e); }
        }
    };

    window.addToMyList = (movieId, btn) => {
        if (!token) return alert("Please sign in to manage your list");
        // Reuse like logic or separate if 'My List' is distinct from 'Like'
        // For now, let's treat it as "Save/Like"
        window.toggleLike(movieId, btn);
    };

    window.openVideoModal = (title) => {
        const modal = document.getElementById('video-modal');
        const titleElem = document.getElementById('video-title');
        titleElem.textContent = title;
        modal.style.display = 'block';
    }

    window.closeVideoModal = () => {
        document.getElementById('video-modal').style.display = 'none';
    }

    window.scrollToSection = (id) => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    }

    // --- Initial Load ---
    await Promise.all([
        renderSection(trendingRow, 'trending'),
        renderSection(newReleasesRow, 'featured')
    ]);
});
