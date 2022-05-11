
/**
 * 
 * Post related action like ['Repost, like and unlike... etc']
 */

/**
 * 
 * @param {Object} selector 
 * @param {String} remove 
 * @param {String} add 
 * @param {String} rmClass 
 * @param {String} adClass 
 * React to certain element given all requeired params, return None
 */
let react = function(selector, remove, add, rmClass, adClass) {
    selector.removeClass(remove).addClass(add).children('i')
    .removeClass(`fa fa-${rmClass}`).addClass(`fa fa-${adClass}`)
}

/**
 * 
 * @param {String} url 
 * @param {Object} messageSelector 
 * Simple function that make an ajax request and get json response
 */
let makeRequest = function(selector, messageSelector, count) {
    $.ajax({
        accepts: 'applications/json',
        url: selector.attr('href'),
    }).done(function(data) {
        if (data.text == null && count) {
            selector.children('.count').text(count)
        } else {
            selector.children('span').text(data.text)
        }
        messageSelector.removeClass('d-none').addClass('d-flex')
        .children('p').text(data.message)
    })
}

/**
 * 
 * @param {Object} selector 
 * @param {String} cls 
 * @param {String} rm 
 * @param {String} add
 * A function that loops though a set of elements and update a specific element based on the [cls] param
 */
let iconeUpdate = function(selector, cls, rm, add) {
    selector.each(function() {
        if ($(this).hasClass(cls)) {
            $(this).removeClass(rm).addClass(add)
        }
    })
}

/**
 * 
 * @param {Object} selector 
 * @param {Object} message 
 * @param {String} rm 
 * @param {String} ad 
 * @param {String} irm 
 * @param {String} i 
 * @param {String} count 
 * @param {Boolean} private
 * @param {Boolean} public
 */

let action = function(selector, message, rm, ad, irm, i, count, private, public) {
    selector.on('click', function(e) {
        e.preventDefault()
        console.log(selector)
        if (count) {
            makeRequest(selector, message, count)
        } else {
            makeRequest(selector, message)
        }
        if (private) {
            let icone = selector.parents('.author').find('i')
            iconeUpdate(icone, 'unlocked', 'fa fa-globe unlocked', 'fa fa-lock lock')
        }
        if (public) {
            let icone = selector.parents('.author').find('i')
            iconeUpdate(icone, 'locked', 'fa fa-lock lock', 'fa fa-globe unlocked')
        }
        react(selector, rm, ad, irm, i)
    })
}

/**
 * JQuery section where posts part is made a little rective
 */

$(function() {
    let post = $('article.post')
    let message = $('.json-message')
    
    post.each(function(i) {
        let unliked = $(this).find('a.unliked')
        let liked = $(this).find('a.liked')
        let reposted = $(this).find('a.reposted')
        let unrepost = $(this).find('a.repost')
        let marked = $(this).find('a.marked')
        let unmarked = $(this).find('a.unmarked')
        let private = $(this).find('a.private')
        let public = $(this).find('a.public')
        let remove = $(this).find('a.delete')

        marked.each(function() {
            action($(this), message, 'marked', 'unmarked', 'bookmark', 'bookmark-o')
        })
        unmarked.each(function() {
            action($(this), message, 'unmarked', 'marked', 'bookmark-o', 'bookmark')
        })
        unliked.each(function() {
            num = Number.parseInt($(this).children('span').text())
            action($(this), message, 'unliked', 'liked', 'heart-o', 'heart liked', `${num + 1}`)
        })
        liked.each(function() {
            num = Number.parseInt($(this).children('span').text())
            action($(this), message, 'liked', 'uliked', 'heart liked', 'heart-o unliked', `${num - 1}`)
        })
        unrepost.each(function() {
            num = Number.parseInt($(this).children('span').text())
            action($(this), message, 'repost main-color', 'reposted link-color', '', '', `${num + 1}`)
        })
        reposted.each(function() {
            num = Number.parseInt($(this).children('span').text())
            action($(this), message, 'reposted link-color', 'repost main-color', '', '', `${num - 1}`)
        })
        private.each(function() {
            action($(this), message, 'ptivate', 'public', 'lock', 'globe', null, true, false)
        })
        public.each(function() {
            action($(this), message, 'public', 'private', 'globe', 'lock', null, false, true)
        })
        remove.each(function() {
            $(this).on('click', function(e) {
                e.preventDefault()
                makeRequest($(this), message)
                $(this).parents('article.post').remove()
            })
        })
    })
})
