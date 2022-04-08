function render_posts(posts)
{
    const postsDiv = document.getElementById('posts');
    const last = postsDiv.children[postsDiv.childElementCount - 1];
    const tail = Object.values(last.children).slice(1, 3);
    const fillc = (tail[0].childElementCount ^ 1) + (tail[1].childElementCount ^ 1);
    const replacediv = tail.slice(tail.length - fillc, tail.length);
    const filll = posts.slice(0, fillc);

    const render = (rows, filll = []) => {
        const createPost = (post) => {
            const postDiv = document.createElement('div');

            postDiv.classList.add('flex');
            postDiv.classList.add('post');

            if (!post.is_fill) {
                postDiv.id = post.node.shortcode;

                const aEle = document.createElement('a');
                aEle.href = `http://localhost:5000/p/${post.node.shortcode}`;

                const overlayDiv = document.createElement('div');
                const tileOneDiv = document.createElement('div');
                const tileTwoDiv = document.createElement('div');
                
                overlayDiv.classList.add('overlay');
                tileOneDiv.innerText = post.node.edge_media_preview_like.count;
                tileOneDiv.classList.add('tile');
                tileTwoDiv.innerText = post.node.edge_media_to_comment.count;
                tileTwoDiv.classList.add('tile');

                overlayDiv.append(tileOneDiv);
                overlayDiv.append(tileTwoDiv);

                const imageDiv = document.createElement('div');
                const imgEle = document.createElement('img');

                imageDiv.classList.add('image');
                imgEle.src = `http://localhost:5000/image?url=${btoa(post.node.thumbnail_src)}`;
                imageDiv.append(imgEle);

                aEle.append(overlayDiv);
                aEle.append(imageDiv);
                postDiv.append(aEle);
            }

            return postDiv;
        };

        const createRow = (row) => {
            const rowDiv = document.createElement('div');

            rowDiv.classList.add('flex');
            rowDiv.classList.add('row');

            for (let posti in row) {
                rowDiv.append(createPost(row[posti]));
            }

            return rowDiv;
        };

        for (let fillli in filll)
            last.replaceChild(createPost(filll[fillli]), replacediv[fillli]);

        for (let rowi in rows) {
            postsDiv.append(createRow(rows[rowi]));
        }
    };

    const fill = (n, p) => {
        for (let i = 0; i < n; i++)
            p.push({"is_fill": true})

        return p
    };

    const sortposts = (posts) => {
        const o = [];
        const c = posts.length;
        let i = 0;

        if (c <= 3) {
            posts = fill(3 - c, posts);
            return [posts];
        }

        while (i < c) {
            o.push(posts.slice(i, i + 3));
            i += 3
        }

        const last = o[o.length - 1];
        o[o.length - 1] = fill(3 - last.length, last);

        return o;
    };

    if (fillc > 0)
        render(sortposts(posts.slice(fillc, posts.length)), filll);
    else
        render(sortposts(posts));
}

async function load_more_posts(e)
{
    const username = e.getAttribute('username');
    const end_cursor = e.getAttribute('end_cursor');
    const data = await fetch(`http://localhost:5000/api/${username}?end_cursor=${end_cursor}`)
        .then((resp) => {
            if (!resp.ok) throw new Error(`HTTP Error: ${resp.status}`);
            return resp.json();
        })
        .then((resp) => {
            return resp;
        });
    
    render_posts(data.edges);

    if (data.page_info.has_next_page) {
        e.href = `#${data.edges[data.edges.length - 1].node.shortcode}`;
        e.setAttribute('end_cursor', data.page_info.end_cursor);
    } else {
        e.style.display = 'none';
    }
}
