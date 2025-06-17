document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed.');

    const calendarEl = document.getElementById('calendar-view');
    const modal = document.getElementById('gratitude-modal');
    const closeModal = document.querySelector('.close-button');
    const modalDateEl = document.getElementById('modal-date');
    const modalGratitudesEl = document.getElementById('modal-gratitudes');



    function getLocalDateString(utcIsoString) {
        const date = new Date(utcIsoString);
        return date.getFullYear() + '-' + String(date.getMonth() + 1).padStart(2, '0') + '-' + String(date.getDate()).padStart(2, '0');
    }

    if (closeModal) {
        closeModal.onclick = () => { modal.style.display = 'none'; };
    }
    window.onclick = (event) => {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    };

    if (calendarEl) {
        console.log('Calendar element found. Fetching gratitudes...');
        fetch('/gratitudes')
            .then(response => response.json())
            .then(allGratitudes => {
                console.log('Gratitudes fetched successfully:', allGratitudes);
                // Log all local date strings for gratitudes
                allGratitudes.forEach(g => {
                    console.log('Gratitude:', g.text, 'UTC timestamp:', g.timestamp, 'Local date string:', getLocalDateString(g.timestamp));
                });

                const calendar = new FullCalendar.Calendar(calendarEl, {
                    initialView: 'dayGridMonth',
                    headerToolbar: {
                        left: 'prev,next today',
                        center: 'title',
                        right: 'dayGridMonth,timeGridWeek,timeGridDay'
                    },
                    dateClick: function(info) {
                        const clickedDate = info.el?.dataset?.date || info.dateStr || (info.date ? info.date.toISOString().slice(0, 10) : undefined);
                        const gratitudesForDay = allGratitudes.filter(g => getLocalDateString(g.timestamp) === clickedDate);
                        if (gratitudesForDay.length > 0) {
                            // Redirect to day-specific view
                            window.location.href = `/gratitude/${clickedDate}`;
                        }
                    },
                    dayCellDidMount: function(info) {
                        // Use the correct date string from the cell's dataset or info.date
                        const cellDateStr = info.el.dataset.date || (info.date ? info.date.toISOString().slice(0, 10) : undefined);
                        console.log('Rendering cell for date:', cellDateStr);
                        const gratitudesForDay = allGratitudes.filter(g => getLocalDateString(g.timestamp) === cellDateStr);
                        if (gratitudesForDay.length > 0) {
                            console.log(`Gratitude found for ${cellDateStr}. Attaching data.`, gratitudesForDay);
                            info.el.classList.add('day-has-gratitude');
                            info.el.dataset.gratitudes = JSON.stringify(gratitudesForDay);
                            // Set pointer cursor and tooltip on the visible frame
                            const tooltipText = gratitudesForDay.map(g => g.text).join('\n');
                            // Set tooltip on all likely targets
                            info.el.title = tooltipText;
                            const frame = info.el.querySelector('.fc-daygrid-day-frame');
                            if (frame) {
                                frame.style.cursor = 'pointer';
                                frame.title = tooltipText;
                            }
                            const number = info.el.querySelector('.fc-daygrid-day-number');
                            if (number) number.title = tooltipText;
                        } else {
                            console.log('No gratitude for', cellDateStr);
                        }
                    }
                });
                console.log('Calendar instance created. Rendering...');
                calendar.render();
                console.log('Calendar rendered.');
            })
            .catch(error => console.error('Error fetching gratitudes:', error));
    }
});
