let page = 2; // Start loading from page 2, as page 1 is already loaded
let loading = false;
let noMorePosts = false;
let feedType = new URLSearchParams(window.location.search).get('feed') || 'trending';

window.addEventListener('scroll', () => {
  if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 200) {
    if (!loading && !noMorePosts) {
      loading = true;
      loadMorePosts();
    }
  }
});

function loadMorePosts() {
  const url = `?page=${page}&feed=${feedType}`;
  const loadingDiv = document.getElementById('loading');
  const noMorePostsDiv = document.getElementById('no-more-posts');
  loadingDiv.style.display = 'block';

  fetch(url, {
    headers: {
      'X-Requested-With': 'XMLHttpRequest'
    }
  })
  .then(response => {
    if (response.ok) {
      return response.json();
    } else {
      throw new Error('No more posts');
    }
  })
  .then(data => {
    if (data.html.trim() === '') {
      noMorePosts = true;
      loadingDiv.style.display = 'none';
      noMorePostsDiv.style.display = 'block';
    } else {
      const postList = document.getElementById('post-list');
      postList.insertAdjacentHTML('beforeend', data.html);
      loadingDiv.style.display = 'none';
      page += 1;
      loading = false;

      if (!data.has_next) {
        noMorePosts = true;
        noMorePostsDiv.style.display = 'block';
      }
    }
  })
  .catch(error => {
    console.error('Error loading more posts:', error);
    loadingDiv.style.display = 'none';
    noMorePosts = true;
    noMorePostsDiv.style.display = 'block';
  });
}
