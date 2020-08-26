(function() {
  "use strict";

  class Progress {
    constructor(settings) {
      this.nodeProgress = settings.nodeProgress;
      this.progressStyles = window.getComputedStyle(this.nodeProgress);
      this.progressSize = parseInt(
        this.progressStyles.getPropertyValue("--uicProgressSize"),
        10
      );
      this.progressValue = settings.progressValue;
      this.progressRadius = settings.progressRadius || 0.4;

      this.progressCircumference = this.getProgressCircumference(
        this.progressRadius,
        this.progressSize
      );
    }

    setProgressValue(newValue) {
      this.progressValue = newValue;
    }

    getProgressCircumference(radius, progressBarSize) {
      return 2 * Math.PI * radius * progressBarSize;
    }

    getProgressGraphValue(progressValue, circumference) {
      return circumference - (progressValue * circumference) / 100;
    }

    convertToEm(value, progressSize) {
      return `${value / progressSize}em`;
    }

    draw() {
      this.nodeProgress.style.setProperty(
        "--uicProgressGraphValue",
        this.convertToEm(
          this.getProgressGraphValue(this.progressValue, this.progressCircumference),
          this.progressSize
        )
      );
    }
  }

  class ProgressBar extends Progress {
    constructor(settings) {
      super({
        nodeProgress: settings.nodeProgress,
        progressValue: settings.progressBarValue
      });
      this.nodeProgressBarValue = settings.nodeProgressBarValue;
      this.draw();
    }

    setProgressBarValue(newValue) {
      super.setProgressValue(newValue);
      this.draw();
    }

    draw() {
      super.draw();
      this.nodeProgressBarValue.textContent = this.progressValue;
    }
  }

  /*
   * demo initialization
   */

  let demoField = document.querySelector(".js-field-value");
  let nodeDemoProgressBar = document.querySelector(".js-progressbar");
  let demoProgressBar = new ProgressBar({
    nodeProgress: nodeDemoProgressBar.querySelector(".js-progressbar__progress"),
    nodeProgressBarValue: nodeDemoProgressBar.querySelector(
      ".js-progressbar__value"
    ),
    // progressBarValue: demoField.value
    progressBarValue: 50
  });

  /* disabling browser's behavior */

  document.querySelector(".js-form").addEventListener("submit", (event) => {
    event.preventDefault();
  });

  /* changing the progress bar value */

  demoField.addEventListener("change", () => {
    if (!demoField.validity.rangeOverflow & !demoField.validity.rangeUnderflow) {
      demoProgressBar.setProgressBarValue(demoField.value);
    }
  });
})();
