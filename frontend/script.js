document.getElementById('login-form').addEventListener('submit', function(e) {
  e.preventDefault();

  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;

  // simulate loading and analysis
  setTimeout(() => {
    const analysis = {
      metrics: {
        posts: 245,
        likes: 12840,
        comments: 920,
        shares: 430,
        reposts: 120
      },
      summary: 'Mostly motivational & informative reels. High engagement on weekends.',
      topHashtags: ['#motivation', '#studyblr', '#reelitfeelit'],
      audience: {
        topLocations: ['Mumbai', 'Bengaluru', 'Delhi'],
        activeHours: ['18:00-20:00', '07:00-09:00']
      }
    };

    // update dashboard
    document.getElementById('posts').innerText = analysis.metrics.posts;
    document.getElementById('likes').innerText = analysis.metrics.likes.toLocaleString();
    document.getElementById('comments').innerText = analysis.metrics.comments;
    document.getElementById('shares').innerText = analysis.metrics.shares;
    document.getElementById('reposts').innerText = analysis.metrics.reposts;
    document.getElementById('hashtags').innerText = analysis.topHashtags.join(', ');
    document.getElementById('summary').innerText = analysis.summary;
    document.getElementById('locations').innerText = analysis.audience.topLocations.join(', ');
    document.getElementById('active-hours').innerText = analysis.audience.activeHours.join(', ');

    document.getElementById('dashboard').style.display = 'block';
  }, 500);
});
