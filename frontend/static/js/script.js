console.log("🚗 AccidentAI Dashboard Loaded");


let previousIncidentCount = 0;
let firstLoad = true;
let alarmPlaying = false;


/* ============================================================
   LOAD INCIDENTS
============================================================ */

async function loadIncidents() {

    try {

        const response = await fetch(
            "/api/incidents?t=" + Date.now()
        );


        if (!response.ok) {
            throw new Error(
                "Incident API failed"
            );
        }


        const incidents =
            await response.json();


        console.log(
            "📋 Incidents:",
            incidents.length
        );


        /* ----------------------------------------------------
           TODAY'S ACCIDENTS
        ---------------------------------------------------- */

        const today =
            new Date()
                .toISOString()
                .split("T")[0];


        const todayIncidents =
            incidents.filter(
                incident =>
                    incident.time &&
                    incident.time.startsWith(today)
            );


        const accidentCount =
            document.getElementById(
                "accident-count"
            );


        if (accidentCount) {

            accidentCount.textContent =
                todayIncidents.length;

        }


        /* ----------------------------------------------------
           ALERT COUNT
        ---------------------------------------------------- */

        const alertCount =
            document.getElementById(
                "alert-count"
            );


        if (alertCount) {

            alertCount.textContent =
                incidents.length;

        }


        /* ----------------------------------------------------
           INCIDENT BADGE
        ---------------------------------------------------- */

        const incidentCount =
            document.getElementById(
                "incident-count"
            );


        if (incidentCount) {

            incidentCount.textContent =
                incidents.length;

        }


        /* ----------------------------------------------------
           INCIDENT LIST
        ---------------------------------------------------- */

        const list =
            document.getElementById(
                "incident-list"
            );


        if (!list) {
            return;
        }


        if (incidents.length === 0) {

            list.innerHTML = `

                <div class="empty-state">

                    <div class="empty-icon">
                        ✓
                    </div>

                    <h4>
                        No accidents detected
                    </h4>

                    <p>
                        AI monitoring is active.
                    </p>

                </div>

            `;

        }
        else {

            const latest =
                [...incidents]
                    .reverse()
                    .slice(0, 10);


            list.innerHTML =
                latest.map(
                    incident => `

                    <div class="incident-item">

                        <div class="incident-left">

                            <div class="incident-danger-icon">
                                🚨
                            </div>

                            <div>

                                <strong>
                                    Accident Confirmed
                                </strong>

                                <p>
                                    Vehicle
                                    ${incident.vehicle_1 ?? "-"}
                                    &
                                    Vehicle
                                    ${incident.vehicle_2 ?? "-"}
                                </p>

                                <small>
                                    🕐
                                    ${incident.time ?? "-"}
                                </small>

                                <small>
                                    📍
                                    ${incident.location ?? "Unknown"}
                                </small>

                            </div>

                        </div>

                        <span class="confirmed">
                            CONFIRMED
                        </span>

                    </div>

                `
                ).join("");

        }


        /* ----------------------------------------------------
           NEW ACCIDENT DETECTED
        ---------------------------------------------------- */

        if (
            !firstLoad &&
            incidents.length >
            previousIncidentCount
        ) {

            const newestIncident =
                incidents[
                    incidents.length - 1
                ];


            console.log(
                "🚨🚨 NEW ACCIDENT CONFIRMED 🚨🚨"
            );


            console.log(
                newestIncident
            );


            showEmergencyAlert(
                newestIncident
            );

        }


        previousIncidentCount =
            incidents.length;


        firstLoad = false;

    }

    catch (error) {

        console.error(
            "❌ Incident loading error:",
            error
        );

    }

}


/* ============================================================
   EMERGENCY ALERT
============================================================ */

function showEmergencyAlert(
    incident
) {

    const alert =
        document.getElementById(
            "emergency-alert"
        );


    if (!alert) {
        return;
    }


    alert.style.display =
        "flex";


    const content =
        alert.querySelector(
            ".emergency-content"
        );


    if (content) {

        content.innerHTML = `

            <h2>
                🚨 EMERGENCY ALERT
            </h2>

            <p>
                <strong>
                    ACCIDENT CONFIRMED BY AI
                </strong>
            </p>

            <p>
                📍
                ${incident.location ?? "Unknown location"}
            </p>

            <p>
                🚗 Vehicle
                ${incident.vehicle_1 ?? "-"}
                &
                Vehicle
                ${incident.vehicle_2 ?? "-"}
            </p>

            <p>
                🕐
                ${incident.time ?? "-"}
            </p>

        `;

    }


    playEmergencyAlarm();

}


/* ============================================================
   ALARM
============================================================ */

function playEmergencyAlarm() {

    const sound =
        document.getElementById(
            "emergency-sound"
        );


    if (!sound) {
        return;
    }


    if (alarmPlaying) {
        return;
    }


    alarmPlaying = true;


    sound.currentTime = 0;
    sound.volume = 1;


    sound.play()

        .then(() => {

            console.log(
                "🔊 Emergency alarm playing"
            );

        })

        .catch(error => {

            console.log(
                "⚠️ Browser blocked alarm:",
                error
            );

            alarmPlaying = false;

        });

}


/* ============================================================
   DISMISS
============================================================ */

const dismissButton =
    document.getElementById(
        "dismiss-alert"
    );


if (dismissButton) {

    dismissButton.addEventListener(
        "click",
        () => {

            const alert =
                document.getElementById(
                    "emergency-alert"
                );


            if (alert) {

                alert.style.display =
                    "none";

            }


            const sound =
                document.getElementById(
                    "emergency-sound"
                );


            if (sound) {

                sound.pause();

                sound.currentTime =
                    0;

            }


            alarmPlaying = false;

        }
    );

}


/* ============================================================
   START AI BUTTON
============================================================ */

const startButton =
    document.getElementById(
        "start-ai-btn"
    );


if (startButton) {

    startButton.addEventListener(
        "click",
        async () => {

            try {

                const response =
                    await fetch(
                        "/api/start-detection",
                        {
                            method: "POST"
                        }
                    );


                const result =
                    await response.json();


                console.log(
                    "🤖 AI:",
                    result
                );


                if (result.success) {

                    startButton.disabled =
                        true;


                    startButton.textContent =
                        "● AI Detection Running";


                    const message =
                        document.getElementById(
                            "detection-message"
                        );


                    if (message) {

                        message.textContent =
                            "AI is analyzing v1.mov for actual collisions.";

                    }

                }
                else {

                    alert(
                        "AI could not start:\n" +
                        result.message
                    );

                }

            }

            catch (error) {

                console.error(
                    error
                );

                alert(
                    "Could not connect to AI detector."
                );

            }

        }
    );

}


/* ============================================================
   STOP AI BUTTON
============================================================ */

const stopButton =
    document.getElementById(
        "stop-ai-btn"
    );


if (stopButton) {

    stopButton.addEventListener(
        "click",
        async () => {

            try {

                await fetch(
                    "/api/stop-detection",
                    {
                        method: "POST"
                    }
                );


                if (startButton) {

                    startButton.disabled =
                        false;

                    startButton.textContent =
                        "▶ Start AI Detection";

                }


                const message =
                    document.getElementById(
                        "detection-message"
                    );


                if (message) {

                    message.textContent =
                        "AI detection stopped.";

                }

            }

            catch (error) {

                console.error(
                    error
                );

            }

        }
    );

}


/* ============================================================
   CHECK AI STATUS
============================================================ */

async function checkAIStatus() {

    try {

        const response =
            await fetch(
                "/api/detection-status?t=" +
                Date.now()
            );


        const result =
            await response.json();


        if (result.running) {

            if (startButton) {

                startButton.disabled =
                    true;

                startButton.textContent =
                    "● AI Detection Running";

            }


            const message =
                document.getElementById(
                    "detection-message"
                );


            if (message) {

                message.textContent =
                    "AI is analyzing v1.mov for actual collisions.";

            }

        }

    }

    catch (error) {

        console.log(
            "AI status unavailable"
        );

    }

}


/* ============================================================
   INITIAL LOAD
============================================================ */

loadIncidents();

checkAIStatus();


/* ============================================================
   CONTINUOUS MONITORING
============================================================ */

setInterval(
    loadIncidents,
    1000
);


setInterval(
    checkAIStatus,
    2000
);