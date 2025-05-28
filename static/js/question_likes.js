function getCookie(name) {
    const cookies = document.cookie.split(';');
    for(let cookie of cookies) {
        const [key, value] = cookie.trim().split('=');
        if(key === name) return decodeURIComponent(value);
    }
    return null;
}

const csrftoken = getCookie('csrftoken');

async function handleVote(url, data, counters) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            body: JSON.stringify(data),
            headers: {
                'X-CSRFToken': csrftoken,
                'Content-Type': 'application/json'
            },
            mode: 'same-origin'
        });

        const result = await response.json();
        // Обновление счетчиков
        console.log(result)
        for(const [selector, valueKey] of Object.entries(counters)) {
            const element = document.querySelector(selector);
            if(element) element.innerHTML = result[valueKey];
        }

        return result;
    } catch(error) {
        console.error('Request failed:', error);
    }
}

function createVoteHandler(type) {
    return function(e) {
        const item = e.currentTarget;
        const id = item.dataset[`q${type}Id`];
        const pos = type === 'like' ? 1 : 0;
        handleVote(
            `/question/${id}/likes`,
            {pos},
            {
                [`span[data-qlike-kol="${id}"]`]: "likes",
                [`span[data-qdislike-kol="${id}"]`]: "dislikes"
            }
        ).then(data => {
            document.querySelector(`button[data-qlike-id="${id}"]`)
                .style.backgroundColor = data.fase === 2 ? '#00CC00' : '#FFFFFF';
            document.querySelector(`button[data-qlike-id="${id}"]`)
                .style.color = data.fase === 2 ?'#FFFFFF'  : '#009900';
            document.querySelector(`button[data-qdislike-id="${id}"]`)
                .style.backgroundColor = data.fase === 1 ? '#FF8888' : '#FFFFFF';
            document.querySelector(`button[data-qdislike-id="${id}"]`)
                .style.color = data.fase === 1 ?'#FFFFFF'  : '#FF0000';
        });
    };
}

function initVoteButtons(selector, type) {
    document.querySelectorAll(selector).forEach(button => {
        button.addEventListener('click', createVoteHandler(type));
    });
}

initVoteButtons('button[data-qlike-id]','like');
initVoteButtons('button[data-qdislike-id]','dislike');