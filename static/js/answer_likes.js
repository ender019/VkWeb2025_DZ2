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
        for(const [selector, valueKey] of Object.entries(counters)) {
            const element = document.querySelector(selector);
            if(element) element.innerHTML = result[valueKey];
        }

        return result;
    } catch(error) {
        console.error('Request failed:', error);
    }
}

function createVoteHandler(type, prefix) {
    return function(e) {
        const item = e.currentTarget;
        const id = item.dataset[`${prefix+type}Id`];
        const pos = type === 'like' ? 1 : 0;

        handleVote(
            `/${prefix === 'q' ? 'question' : 'answer'}/${id}/likes`,
            {pos},
            {
                [`span[data-${prefix}like-kol="${id}"]`]: "likes",
                [`span[data-${prefix}dislike-kol="${id}"]`]: "dislikes"
            }
        ).then(data => {
            document.querySelector(`button[data-${prefix}like-id="${id}"]`)
                .style.backgroundColor = data.fase === 2 ? '#00CC00' : '#FFFFFF';
            document.querySelector(`button[data-${prefix}like-id="${id}"]`)
                .style.color = data.fase === 2 ?'#FFFFFF'  : '#009900';
            document.querySelector(`button[data-${prefix}dislike-id="${id}"]`)
                .style.backgroundColor = data.fase === 1 ? '#FF8888' : '#FFFFFF';
            document.querySelector(`button[data-${prefix}dislike-id="${id}"]`)
                .style.color = data.fase === 1 ?'#FFFFFF'  : '#FF0000';
        });
    };
}

function handleCorrect(e) {
    const item = e.target;
    fetch(`/answer/${item.dataset.correctId}/correct`, {
        method: 'POST',
        body: JSON.stringify({"cor": !item.checked}),
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/json'
        },
        mode: 'same-origin'
    });
}

function initVoteButtons(selector, prefix, type) {
    document.querySelectorAll(selector).forEach(button => {
        button.addEventListener('click', createVoteHandler(type, prefix));
    });
}

initVoteButtons('button[data-alike-id]', 'a', 'like');
initVoteButtons('button[data-adislike-id]', 'a', 'dislike');
initVoteButtons('button[data-qlike-id]', 'q', 'like');
initVoteButtons('button[data-qdislike-id]', 'q', 'dislike');

document.querySelectorAll('input[data-correct-id]').forEach(item => {
    item.addEventListener('change', handleCorrect);
});