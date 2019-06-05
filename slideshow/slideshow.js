var MAX_SLIDES = 10;
var initialized = false;
var rangeStart = 0;
var currentSlideInRange = 0;
var pictures = []

function addSlide(n) {
  // We're creating this guy
  // <div class="mySlides fade">
  // <!-- <div class="numbertext">1 / 3</div> -->
  // <img src="../pictures/GOPR4805.jpg" style="width:100%">
  // <div class="text">1 / 3</div>
  // </div>

  var element = document.createElement('div');
  element.id = 'slide-' + n;
  element.className = 'mySlides'; // fade';

  var textBlock = document.createElement('div');
  textBlock.className = 'text';
  textBlock.appendChild(document.createTextNode((n+1) + ' / ' + pictures.length));
  element.appendChild(textBlock);

  var imgBlock = document.createElement('img');
  imgBlock.style = 'width: 100%;';
  imgBlock.src = '/pictures/' + pictures[n];
  element.appendChild(imgBlock);

  document.getElementById('slide-container').appendChild(element);
}

function updateSlides() {
  var slides = document.getElementsByClassName('mySlides');
  while (slides.length != 0 ) {
    slides[0].parentNode.removeChild(slides[0]);
  }

  for (var i = 0; i < pictures.length; i++) {
    addSlide(i);
  }


  setRange(rangeStart);
  setSlideInRange(currentSlideInRange);

  if (!initialized) {
    rangeStart = Math.floor((pictures.length - 1) / MAX_SLIDES) * MAX_SLIDES;
    setSlideInRange((pictures.length - 1) % MAX_SLIDES);
    initialized = true;
  }
}

function changeRange(diff) {
  var newRangeStart = rangeStart + diff * MAX_SLIDES;
  setRange(newRangeStart);

  if (diff < 0) {
    setSlideInRange(MAX_SLIDES - 1);
  } else {
    setSlideInRange(0);
  }
}

function setRange(rangeNumber) {
  rangeStart = rangeNumber;

  var moredots = document.getElementsByClassName('moredot');
  var dots = document.getElementsByClassName('dot');
  if (rangeStart == 0) {
    moredots[0].style.display = 'none';
  } else {
    moredots[0].style.display = 'inline-block';
  }

  if (rangeStart + MAX_SLIDES >= pictures.length) {
    moredots[1].style.display = 'none';
  } else {
    moredots[1].style.display = 'inline-block';
  }

  for (var i = 0; i < MAX_SLIDES; i++) {
    if (rangeStart + i < pictures.length) {
      dots[i].style.display = 'inline-block';
    } else {
      dots[i].style.display = 'none';
    }
  }
}

function changeSlideInRange(diff) {
  var slideNumber = currentSlideInRange + diff;
  var newRangeStart = rangeStart;
  if (slideNumber < 0) {
    if (rangeStart - MAX_SLIDES < 0) {
      return;
    } else {
      newRangeStart = rangeStart - MAX_SLIDES;
      slideNumber = MAX_SLIDES - 1;
    }
  } else if (slideNumber >= MAX_SLIDES || rangeStart + slideNumber >= pictures.length) {
    if (rangeStart + MAX_SLIDES >= pictures.length) {
      return;
    } else {
      newRangeStart = rangeStart + MAX_SLIDES;
      slideNumber = 0;
    }
  }

  if (newRangeStart != rangeStart) {
    setRange(newRangeStart);
  }
  setSlideInRange(slideNumber);
}

function setSlideInRange(slideNumber) {
  currentSlideInRange = slideNumber;
  var slides = document.getElementsByClassName('mySlides');
  var dots = document.getElementsByClassName('dot');

  for (var i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  for (var i = 0; i < dots.length; i++) {
    dots[i].className = dots[i].className.replace(" active", "");
  }

  slides[rangeStart + currentSlideInRange].style.display = "block";
  dots[currentSlideInRange].className += " active";
}

// Refresh as pictures come in
(function worker() {
  $.ajax({
    url: '/pictures.json',
    success: function(data) {
      pictures = data
      updateSlides();
    },
    complete: function() {
      // Schedule the next request when the current one's complete
      setTimeout(worker, 1000);
    }
  });
})();
